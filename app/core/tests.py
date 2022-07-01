from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class ModelTests(TestCase):
    def test_create_user_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'sad@sad.com'
        password = 'saddem123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'test@LONDONAPPDEV.com'
        user = get_user_model().objects.create_user(email, 'test123')
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'saddem123')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            email='sad@sad.com',
            password='saddem123'
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


class AdminSiteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="sad@sad.com",
            password="saddem123"
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='test@test.com',
            password='saddem123',
            name="TEST"
        )

    def test_users_listed(self):
        """Test that users are listed on user page"""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)
