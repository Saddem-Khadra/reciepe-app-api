from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from core.models import User

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**kwargs: dict) -> User:
    return get_user_model().objects.create_user(**kwargs)


class PublicUserApiTests(TestCase):
    """Test the users API (public)"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_valid_user_success(self) -> None:
        """Test creating user valid payload is successful"""
        payload = {
            'email': 'sad@sad.com',
            'password': 'saddem123',
            'name': 'SADD'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self) -> None:
        """Test creating a user that already exists fails"""
        payload = {
            'email': 'sad@sad.com',
            'password': 'saddem123',
            'name': 'SADD'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self) -> None:
        """Test that the password must be more than 5 characters"""
        payload = {
            'email': 'sad@sad.com',
            'password': 'sadd',
            'name': 'SADD'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self) -> None:
        """Test that a token is created for the user"""
        payload = {
            'email': 'sad@sad.com',
            'password': 'saddem123',
            'name': 'SADD'
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self) -> None:
        """Test that token is not created if invalid credentials are given"""
        payload = {
            'email': 'sad@sad.com',
            'password': 'testpass',
            'name': 'SADD'
        }
        create_user(**payload)
        payload = {
            'email': 'sad@sad.com',
            'password': 'saddem123',
            'name': 'SADD'
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self) -> None:
        """Test that token is not created if user doesn't exist"""
        payload = {
            'email': 'sad@sad.com',
            'password': 'testpass',
            'name': 'SADD'
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_missing_field(self) -> None:
        """Test that email and password are required"""
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self) -> None:
        """Test that authentication is required for users"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API that require authentication"""

    def setUp(self) -> None:
        payload = {
            'email': 'sad@sad.com',
            'password': 'testpass',
            'name': 'SADD'
        }
        self.user = create_user(**payload)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self) -> None:
        """Test retrieving profile for logged un used"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {'name': self.user.name, 'email': self.user.email})

    def test_post_me_not_allowed(self) -> None:
        """Test that POST is not allowed on the me url"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self) -> None:
        """Test updating the user profile for authenticated user"""
        payload = {
            'email': 'sad@sad.com',
            'password': 'newtestpass',
            'name': 'newSADD'
        }
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
