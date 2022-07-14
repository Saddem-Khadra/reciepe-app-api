from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Recipe, Tag, Ingredient, User
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id: int) -> reverse:
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user: User, name: str = 'Main course') -> Tag:
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user: User, name: str = 'Cinnamon') -> Ingredient:
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user: User, **kwargs: dict) -> Recipe:
    """Create and return a smple recipe"""
    payload: dict = {'title': 'Sample recipe', 'time_minutes': 10, 'price': 5.00}
    payload.update(kwargs)
    return Recipe.objects.create(user=user, **payload)


class PublicRecipeTest(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self) -> None:
        """Test that authentication is required"""
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self) -> None:
        payload = {
            'email': 'sad@sad.com',
            'password': 'testpass',
            'name': 'SADD'
        }
        self.user = get_user_model().objects.create_user(**payload)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_recipes(self):
        """Test retrieveing recipes"""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)
        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test that recipes returned are for the authenticated user"""
        user2 = get_user_model().objects.create_user("khad@khad.com", "khadra123")
        sample_recipe(user=user2)
        sample_recipe(user=self.user)
        res = self.client.get(RECIPE_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))
        url = detail_url(recipe.id)
        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
