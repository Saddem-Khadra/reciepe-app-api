from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from core.models import User


def sample_user(email='sad@sad.com', password='saddem123') -> User:
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

    def test_ingredient_str(self) -> None:
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(user=sample_user(), name='Cucumber')
        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self) -> None:
        """Test the recipe string representation"""
        recipe = models.Recipe.objects.create(
            user=sample_user(),
            title='Steak and mushroom sauce',
            time_minutes=5,
            price=5.00
        )
        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test that images is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')
        exp_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)
