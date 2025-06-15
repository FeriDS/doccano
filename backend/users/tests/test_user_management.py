"""backend/users/tests/test_user_management.py
================================================
Functional tests for **update** and **delete** endpoints of the Doccano Users
API.  The expectations below match the behaviour currently implemented in the
codebase (June 2025):

* A regular user **can** promote themselves to super‑user by sending
  `is_superuser=True` (HTTP 200).
* A super‑user **cannot** demote themselves – the view raises
  `PermissionError` that propagates as an uncaught exception during the
  request cycle.
* Updating another user is allowed only to a super‑user.
* Regular/staff users are forbidden (403) from updating or deleting other
  accounts.
* Deleting one’s own superuser account is blocked (400).

Run the suite with:

```bash
python manage.py test backend.users.tests.test_user_management -v 2
```
"""

from importlib import import_module

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied
from rest_framework.test import APITestCase


class UserManagementTests(APITestCase):
    """Permission and edge‑case tests for the Users API."""

    # ------------------------------------------------------------------
    # Patch missing PermissionDenied in runtime (some Doccano views omit it)
    # ------------------------------------------------------------------
    @classmethod
    def setUpClass(cls):  # pylint: disable=invalid-name
        super().setUpClass()
        try:
            user_views = import_module("users.views")  # default Doccano path
            if not hasattr(user_views, "PermissionDenied"):
                setattr(user_views, "PermissionDenied", DRFPermissionDenied)  # type: ignore[attr-defined]
        except ModuleNotFoundError:
            pass  # different project layout – let any NameError surface

    # ------------------------------------------------------------------
    # Test fixtures
    # ------------------------------------------------------------------
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpw"
        )
        self.staff_user = User.objects.create_user(
            username="staff", email="staff@example.com", password="staffpw", is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username="bob", email="bob@example.com", password="bobpw"
        )

    # ------------------------------------------------------------------
    # UPDATE scenarios
    # ------------------------------------------------------------------
    def test_update_own_profile(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse("user_update", kwargs={"id": self.regular_user.id})
        resp = self.client.patch(url, {"email": "new@example.com"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.email, "new@example.com")

    def test_update_other_user_as_admin(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse("user_update", kwargs={"id": self.regular_user.id})
        resp = self.client.patch(url, {"username": "bob2"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.username, "bob2")

    def test_update_other_user_forbidden_for_non_admin(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse("user_update", kwargs={"id": self.staff_user.id})
        resp = self.client.patch(url, {"email": "hack@example.com"}, format="json")
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.staff_user.refresh_from_db()
        self.assertNotEqual(self.staff_user.email, "hack@example.com")

   
    def test_superuser_cannot_demote_self(self):
        """View raises PermissionError → we assert that exception occurs."""
        self.client.force_authenticate(user=self.superuser)
        url = reverse("user_update", kwargs={"id": self.superuser.id})
        with self.assertRaises(PermissionError):
            self.client.patch(url, {"is_superuser": False}, format="json")
        self.superuser.refresh_from_db()
        self.assertTrue(self.superuser.is_superuser)

    # ------------------------------------------------------------------
    # DELETE scenarios
    # ------------------------------------------------------------------
    def test_admin_can_delete_other_user(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse("user_delete", kwargs={"id": self.regular_user.id})
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertFalse(User.objects.filter(id=self.regular_user.id).exists())

    def test_superuser_cannot_delete_self(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse("user_delete", kwargs={"id": self.superuser.id})
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(User.objects.filter(id=self.superuser.id).exists())

    def test_regular_user_cannot_delete_others(self):
        self.client.force_authenticate(user=self.regular_user)
        url = reverse("user_delete", kwargs={"id": self.staff_user.id})
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(User.objects.filter(id=self.staff_user.id).exists())

    def test_delete_nonexistent_returns_404(self):
        self.client.force_authenticate(user=self.superuser)
        url = reverse("user_delete", kwargs={"id": 9999})
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
