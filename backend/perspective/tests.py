from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from .models import Perspective
from projects.models import Project  # Se houver relação com projetos

class PerspectivePermissionsTests(APITestCase):
    def setUp(self):
        # Cria usuários para teste
        self.admin = User.objects.create_user(
            username='admin',
            password='testpass123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            password='testpass123'
        )
        
        # Cria dados de teste
        self.perspective = Perspective.objects.create(
            name="Test Perspective",
            description="Test Description"
        )

    def test_list_perspectives_as_admin(self):
        """Testa se admin pode listar perspetivas"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/perspective/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_perspectives_as_regular_user(self):
        """Testa se usuário normal pode listar perspetivas"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get('/api/perspective/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthenticated_access(self):
        """Testa acesso não autenticado"""
        response = self.client.get('/api/perspective/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class PerspectiveAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Dados compartilhados entre todos os testes da classe
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        cls.perspective = Perspective.objects.create(
            name="Sample Perspective",
            description="Sample Description"
        )

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_perspective_list(self):
        """Testa a listagem de perspetivas"""
        response = self.client.get('/api/perspective/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Verifica se retorna 1 item

    def test_perspective_detail(self):
        """Testa a visualização de detalhes"""
        url = f'/api/perspective/{self.perspective.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Sample Perspective")

    def test_perspective_filtering(self):
        """Testa filtros por nome"""
        Perspective.objects.create(name="Work", description="Work related")
        response = self.client.get('/api/perspective/?name=Work')
        self.assertEqual(len(response.data), 1)

    def test_perspective_ordering(self):
        """Testa ordenação por data"""
        Perspective.objects.create(name="Newer", description="Created later")
        response = self.client.get('/api/perspective/?ordering=-created_at')
        self.assertEqual(response.data[0]['name'], "Newer")
    
    def test_perspective_with_projects(self):
        """Testa se projetos associados são retornados"""
        project = Project.objects.create(name="Test Project")
        self.perspective.projects.add(project)
        
        response = self.client.get(f'/api/perspective/{self.perspective.id}/')
        self.assertEqual(len(response.data['projects']), 1)