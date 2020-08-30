from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'test@max.net'
        password = 'Test1234'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_norm(self):
        """Test the email is normalised"""
        email = 'test@MAX.NET'
        user = get_user_model().objects.create_user(email, 'asdf')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user without email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'asdf')

    def test_superuser_created(self):
        """Test create a new superuser"""
        user = get_user_model().objects.create_superuser(
               'test@max.net',
               'asdf'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
