from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def sample_user(email='sad@sad.com', password='saddem123'):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    def test_create_user_email_successful(self) -> None:
        """Test creating a new user with an email is successful"""
        email = 'sad@sad.com'
        password = 'saddem123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self) -> None:
        """Test the email for a new user is normalized"""
        email = 'test@LONDONAPPDEV.com'
        user = get_user_model().objects.create_user(email, 'test123')
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self) -> None:
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'saddem123')

    def test_create_new_superuser(self) -> None:
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            email='sad@sad.com',
            password='saddem123'
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_tag_str(self) -> None:
        """Test the tag string representation"""
        tag = models.Tag.objects.create(user=sample_user(), name='Vegan')
        self.assertEqual(str(tag), tag.name)
