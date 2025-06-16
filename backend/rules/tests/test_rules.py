"""
Testes para o sistema de votação de regras.

Este arquivo contém testes para verificar o fluxo completo de votação
de regras no sistema. Os testes cobrem os seguintes casos de uso:

1. Consultar votação final das regras de anotação
2. Votar nas regras de anotação
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from projects.models import Project, Member
from roles.models import Role
from rules.models import Rule, ProjectRule, RuleVote

User = get_user_model()

class RuleVotingTests(TestCase):
    def setUp(self):
        # Criar usuários
        self.u1 = User.objects.create_user(username="u1", password="p1", is_staff=True, is_superuser=True)
        self.u2 = User.objects.create_user(username="u2", password="p2")
        self.u3 = User.objects.create_user(username="u3", password="p3")
        
        # Criar projeto
        self.project = Project.objects.create(
            name="Test Project",
            project_type="DocumentClassification",
            random_order=False,
            collaborative_annotation=True,
            single_class_classification=False,
            created_by=self.u1
        )
        
        # Criar papéis
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
        Member.objects.create(
            user=self.u3,
            project=self.project,
            role=self.annotator_role
        )
        
        # Criar regras
        self.rule1 = Rule.objects.create(
            text="Regra de teste 1"
        )
        self.rule2 = Rule.objects.create(
            text="Regra de teste 2"
        )
        
        # Adicionar regras ao projeto
        self.project_rule1 = ProjectRule.objects.create(
            project=self.project,
            rule=self.rule1
        )
        self.project_rule2 = ProjectRule.objects.create(
            project=self.project,
            rule=self.rule2
        )
        
        # Configurar cliente API
        self.client = APIClient()
        self.client.force_authenticate(user=self.u1)

    def test_list_rules_with_votes(self):
        """Testa a listagem de regras com suas votações."""
        # Fazer alguns votos
        RuleVote.objects.create(
            project_rule=self.project_rule1,
            user=self.u1,
            vote=True
        )
        RuleVote.objects.create(
            project_rule=self.project_rule1,
            user=self.u2,
            vote=False
        )
        RuleVote.objects.create(
            project_rule=self.project_rule2,
            user=self.u1,
            vote=True
        )
        
        # Listar regras
        url = reverse("project-rule-list", args=[self.project.id])
        resp = self.client.get(url)
        
        # Debug: imprimir informações sobre as regras
        print("\nDebug info:")
        print(f"Total rules in database: {Rule.objects.count()}")
        print(f"Total project rules in database: {ProjectRule.objects.count()}")
        print("Project rules in response:")
        print(f"Response data: {resp.data}")
        
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 2, f"Expected 2 rules, got {resp.data['count']}")
        
        # Verificar regra 1
        rule1_data = next(r for r in resp.data['results'] if r["rule"]["id"] == self.rule1.id)
        self.assertEqual(rule1_data["votes_yes"], 1)
        self.assertEqual(rule1_data["votes_no"], 1)
        self.assertTrue(rule1_data["user_has_voted"])
        self.assertTrue(rule1_data["vote"])
        
        # Verificar regra 2
        rule2_data = next(r for r in resp.data['results'] if r["rule"]["id"] == self.rule2.id)
        self.assertEqual(rule2_data["votes_yes"], 1)
        self.assertEqual(rule2_data["votes_no"], 0)
        self.assertTrue(rule2_data["user_has_voted"])
        self.assertTrue(rule2_data["vote"])

    def test_vote_on_rule(self):
        """Testa o processo de votação em uma regra."""
        # Votar na regra 1
        url = reverse("project-rule-vote", args=[self.project.id, self.rule1.id])
        resp = self.client.post(url, {"vote": True}, format="json")
        
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["votes_yes"], 1)
        self.assertEqual(resp.data["votes_no"], 0)
        self.assertTrue(resp.data["user_has_voted"])
        self.assertTrue(resp.data["is_open"])
        
        # Verificar se o voto foi registrado
        self.assertTrue(
            RuleVote.objects.filter(
                project_rule=self.project_rule1,
                user=self.u1,
                vote=True
            ).exists()
        )
        
        # Mudar o voto
        resp = self.client.post(url, {"vote": False}, format="json")
        
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["votes_yes"], 0)
        self.assertEqual(resp.data["votes_no"], 1)
        self.assertTrue(resp.data["user_has_voted"])
        
        # Verificar se o voto foi atualizado
        self.assertTrue(
            RuleVote.objects.filter(
                project_rule=self.project_rule1,
                user=self.u1,
                vote=False
            ).exists()
        )

    def test_bulk_vote_on_rules(self):
        """Testa o processo de votação em múltiplas regras de uma vez."""
        url = reverse("project-bulk-rule-vote", args=[self.project.id])
        resp = self.client.post(
            url,
            {
                "votes": [
                    {"rule_id": self.rule1.id, "vote": True},
                    {"rule_id": self.rule2.id, "vote": False}
                ]
            },
            format="json"
        )
        
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(resp.data["results"]), 2)
        
        # Verificar se os votos foram registrados
        self.assertTrue(
            RuleVote.objects.filter(
                project_rule=self.project_rule1,
                user=self.u1,
                vote=True
            ).exists()
        )
        self.assertTrue(
            RuleVote.objects.filter(
                project_rule=self.project_rule2,
                user=self.u1,
                vote=False
            ).exists()
        )

    def test_vote_on_closed_rule(self):
        """Testa tentativa de votar em uma regra com votação encerrada."""
        # Fechar a votação da regra 1
        self.project_rule1.is_open = False
        self.project_rule1.save()
        
        # Tentar votar
        url = reverse("project-rule-vote", args=[self.project.id, self.rule1.id])
        resp = self.client.post(url, {"vote": True}, format="json")
        
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data["error"], "Votação encerrada.") 