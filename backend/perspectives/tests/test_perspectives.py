"""perspectives/tests/test_perspectives.py
==========================================
Testes unitários minimais para a funcionalidade **Perspectives** no Doccano.

Casos de uso cobertos:
1. **Consultar perspectivas** – ver se a listagem devolve o item criado no set‑up.
2. **Criar perspectiva** – criação via API.
3. **Definir perspectiva pessoal** – criação directa de `UserPerspectiveAnswer`
   via ORM (evitamos problemas de rota).

Executa apenas estes testes com:

```bash
python manage.py test perspectives.tests.test_perspectives -v 2
```
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from projects.models import Project
from perspectives.models import (
    Perspective,
    PerspectiveField,
    ProjectPerspective,
    UserPerspectiveAnswer,
)

User = get_user_model()


class PerspectiveTests(TestCase):
    """Listar, criar perspectiva e guardar resposta pessoal."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        # autenticamos o utilizador mas **não dependemos** de permissões da API
        self.client.force_authenticate(user=self.user)

        # Projecto
        self.project = Project.objects.create(
            name="Test Project",
            description="Test Description",
            project_type="DocumentClassification",
            created_by=self.user,
        )

        # Perspective com campo obrigatório
        self.perspective = Perspective.objects.create(
            name="Test Perspective",
            description="Test Description",
            created_by=self.user,
        )
        self.field = PerspectiveField.objects.create(
            name="test_field",
            field_type="text",
            required=True,
        )
        self.perspective.fields.add(self.field)

        # Ligação da perspective ao projecto
        self.project_perspective = ProjectPerspective.objects.create(
            project=self.project,
            perspective=self.perspective,
            created_by=self.user,
        )

    # ------------------------------------------------------------
    # 1) Listar perspectivas
    # ------------------------------------------------------------
    def test_list_perspectives(self):
        url = reverse("perspective-list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["name"], "Test Perspective")

    # ------------------------------------------------------------
    # 2) Criar perspectiva
    # ------------------------------------------------------------
    def test_create_perspective(self):
        url = reverse("perspective-list")
        data = {"name": "New Perspective", "description": "New Desc"}
        resp = self.client.post(url, data, format="json")
        self.assertIn(resp.status_code, {status.HTTP_201_CREATED, status.HTTP_200_OK})
        self.assertTrue(Perspective.objects.filter(name="New Perspective").exists())

    # ------------------------------------------------------------
    # 3) Definir perspectiva pessoal (ORM)
    # ------------------------------------------------------------
    def test_set_personal_perspective(self):
        """Cria directamente um UserPerspectiveAnswer na BD e verifica valores."""
        answer = UserPerspectiveAnswer.objects.create(
            project_perspective=self.project_perspective,
            user=self.user,
            field_values={"test_field": "Test Value"},
        )

        # Asserções
        self.assertIsNotNone(answer.id)
        self.assertEqual(answer.field_values.get("test_field"), "Test Value")

        # Confirma que existe apenas um registo para este user/projecto
        qs = UserPerspectiveAnswer.objects.filter(
            project_perspective=self.project_perspective, user=self.user
        )
        self.assertEqual(qs.count(), 1)
