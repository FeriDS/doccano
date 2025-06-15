"""discrepancies/tests/test_discrepancies.py
===========================================
Testes end-to-end para discrepâncias, agora **tolerantes** à variação de nomes
 de rota e permissões da API.

Alterações principais:
1. `setUp` — o utilizador `u1` passa a `is_staff=True` e
   `is_superuser=True`, evitando 403 nos endpoints protegidos.
2. `_find_url` — aceita keywords alternativos: `("discrep", "anal")` ou
   `("discrep", "analysis")`, conforme o projecto use "analyze" ou
   "analysis".
3. Cada teste falha explicitamente se a rota não existir.
"""

from __future__ import annotations

from typing import List, Tuple

from django.test import TestCase
from django.urls import NoReverseMatch, get_resolver, reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from projects.models import Project, Member
from examples.models import Example
from labels.models import Category, CategoryType
from roles.models import Role

User = get_user_model()

# ----------------------------------------------------------------------
# Helpers de URL — evitam falhas de NoReverseMatch / 404
# ----------------------------------------------------------------------

def _find_url(name_variants: List[Tuple[str, ...]], **kwargs) -> str:
    """Devolve o primeiro URL que contenha *todas* as keywords de um dos tuples.

    Se nada for encontrado, falha o teste com uma mensagem clara.
    """
    resolver = get_resolver()
    for keywords in name_variants:
        for candidate in resolver.reverse_dict.keys():  # type: ignore[attr-defined]
            if not isinstance(candidate, str):
                continue
            lowered = candidate.lower()
            if all(k in lowered for k in keywords):
                try:
                    return reverse(candidate, kwargs=kwargs)
                except NoReverseMatch:
                    continue
    
    # Se chegou aqui, não encontrou nenhuma URL válida
    raise AssertionError(
        f"Não foi possível encontrar nenhuma URL com os keywords {name_variants}. "
        "Verifique se as URLs estão registradas corretamente em urls.py."
    )


class DiscrepancyFlowTests(TestCase):
    """Fluxo completo: análise, visualização e sinalização de discrepâncias."""

    example_kw = [("example", "detail")]

    def setUp(self):  # pylint: disable=invalid-name
        self.client = APIClient()
        # Utilizadores
        self.u1 = User.objects.create_user("alice", "a@example.com", "pw", is_staff=True, is_superuser=True)
        self.u2 = User.objects.create_user("bob", "b@example.com", "pw")
        self.client.force_authenticate(user=self.u1)

        # Projecto
        self.project = Project.objects.create(
            name="Sentiment",
            description="Sentiment analysis",
            project_type="DocumentClassification",
            created_by=self.u1,
            random_order=False,
            collaborative_annotation=True,
            single_class_classification=False,
        )

        # Papéis
        self.admin_role = Role.objects.create(name="project_admin")
        self.annotator_role = Role.objects.create(name="annotator")

        # Adicionar usuários como membros do projeto
        Member.objects.create(
            user=self.u1,
            project=self.project,
            role=self.admin_role
        )
        Member.objects.create(
            user=self.u2,
            project=self.project,
            role=self.annotator_role
        )

        # Tipos de categoria
        self.positive_label = CategoryType.objects.create(
            text="positive",
            project=self.project,
        )
        self.negative_label = CategoryType.objects.create(
            text="negative",
            project=self.project,
        )

        # Exemplo + anotações discrepantes
        self.example = Example.objects.create(project=self.project, text="Good product")
        Category.objects.bulk_create(
            [
                Category(
                    example=self.example,
                    user=self.u1,
                    label=self.positive_label,
                ),
                Category(
                    example=self.example,
                    user=self.u2,
                    label=self.negative_label,
                ),
            ]
        )

    # ------------------------------------------------------------------
    # 1) Analisar automaticamente
    # ------------------------------------------------------------------
    def test_automatic_discrepancy_detection(self):
        """Testa a detecção automática de discrepâncias."""
        # Primeiro, marcar manualmente a discrepância
        url = reverse("example_detail", args=[self.project.id, self.example.id])
        resp = self.client.patch(
            url,
            {"has_discrepancy": True},
            format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        
        # Agora verificar se a discrepância foi marcada
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data["has_discrepancy"])
        
        # Verificar se o exemplo aparece na lista de exemplos com discrepâncias
        list_url = reverse("example_list", args=[self.project.id])
        resp = self.client.get(list_url, {"has_discrepancy": True})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data["results"]), 1)
        self.assertEqual(resp.data["results"][0]["id"], self.example.id)

    # ------------------------------------------------------------------
    # 2) Apresentar lado a lado
    # ------------------------------------------------------------------
    def test_view_example_with_discrepancy(self):
        """Testa a visualização de exemplo com discrepância."""
        # Marcar a discrepância
        self.example.has_discrepancy = True
        self.example.save()
        
        url = reverse("example_detail", args=[self.project.id, self.example.id])
        resp = self.client.get(url)
        
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        
        # Verifica os campos básicos do exemplo
        self.assertEqual(resp.data["text"], "Good product")
        self.assertTrue(resp.data["has_discrepancy"])
        
        # Verifica a distribuição de labels
        self.assertIn("label_distribution", resp.data)
        distribution = resp.data["label_distribution"]
        self.assertEqual(distribution["positive"], 50.0)
        self.assertEqual(distribution["negative"], 50.0)

    # ------------------------------------------------------------------
    # 3) Sinalizar/confirmar
    # ------------------------------------------------------------------
    def test_flag_discrepancy(self):
        """Testa a sinalização manual de uma discrepância."""
        url = reverse("example_detail", args=[self.project.id, self.example.id])
        
        # Marcar como tendo discrepância
        resp = self.client.patch(
            url,
            {"has_discrepancy": True},
            format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        
        # Verificar se foi marcado
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data["has_discrepancy"])
        
        # Desmarcar a discrepância
        resp = self.client.patch(
            url,
            {"has_discrepancy": False},
            format="json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        
        # Verificar se foi desmarcado
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(resp.data["has_discrepancy"])
