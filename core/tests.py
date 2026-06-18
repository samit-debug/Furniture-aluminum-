from django.contrib.auth import authenticate, get_user_model
from django.test import TestCase
from django.urls import reverse


class EmailOrUsernameBackendTests(TestCase):
    def test_email_login_trims_identifier(self):
        User = get_user_model()
        User.objects.create_user(username="owner", email="owner@example.com", password="strong-pass-123")

        user = authenticate(username="  OWNER@example.com  ", password="strong-pass-123")

        self.assertIsNotNone(user)
        self.assertEqual(user.username, "owner")

    def test_duplicate_email_can_match_correct_password(self):
        User = get_user_model()
        User.objects.create_user(username="first", email="team@example.com", password="first-pass-123")
        User.objects.create_user(username="second", email="team@example.com", password="second-pass-123")

        user = authenticate(username="team@example.com", password="second-pass-123")

        self.assertIsNotNone(user)
        self.assertEqual(user.username, "second")


class AdminControlTests(TestCase):
    def test_admin_control_renders_for_superuser(self):
        User = get_user_model()
        user = User.objects.create_superuser(
            username="rajesh",
            email="rajesh@example.com",
            password="strong-pass-123",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("admin-control"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Owner Control")

    def test_admin_control_redirects_non_admin_user(self):
        User = get_user_model()
        user = User.objects.create_user(username="staff", password="strong-pass-123")
        self.client.force_login(user)

        response = self.client.get(reverse("admin-control"))

        self.assertRedirects(response, reverse("dashboard"))
