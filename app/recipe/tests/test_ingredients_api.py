from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer

INGR_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """Test publicly available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required to access the API endpoint"""
        res = self.client.get(INGR_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test the private ingredients API"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@mglabs.lv',
            'tstpass123'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        """Retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')

        res = self.client.get(INGR_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients for the authenticated user are returned"""
        user2 = get_user_model().objects.create_user('other@mglabs.lv',
                                                     'testpass3432')
        Ingredient.objects.create(user=user2, name='Vinegar')

        ingr = Ingredient.objects.create(user=self.user, name='Tumeric')

        res = self.client.get(INGR_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingr.name)

    def test_create_ingredient_successfull(self):
        """Test creation of a new ingredient"""
        payload = {'name': 'Cabbage'}
        self.client.post(INGR_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name'],
        ).exists()

        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test creation of a new ingredient fails"""
        payload = {'name': ''}
        res = self.client.post(INGR_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """Test filtering ingredients by those assigned to recipes"""
        ing1 = Ingredient.objects.create(user=self.user, name='Apples')
        ing2 = Ingredient.objects.create(user=self.user, name='Turkey')
        recipe = Recipe.objects.create(
            title='Apple crumble',
            time_minutes=6,
            price=9.87,
            user=self.user
        )

        recipe.ingredients.add(ing1)
        res = self.client.get(INGR_URL, {'assigned_only': 1})

        ser1 = IngredientSerializer(ing1)
        ser2 = IngredientSerializer(ing2)

        self.assertIn(ser1.data, res.data)
        self.assertNotIn(ser2.data, res.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """Test filtering ingredients by assigned return unique items"""
        ing = Ingredient.objects.create(
            name='Eggs',
            user=self.user
        )
        Ingredient.objects.create(user=self.user, name='Cheese')

        recp1 = Recipe.objects.create(
            title='Eggs Benedict',
            time_minutes=30,
            price=19.00,
            user=self.user
        )
        recp1.ingredients.add(ing)
        recp2 = Recipe.objects.create(
            title='Corriander eggs on toast',
            time_minutes=20,
            price=5.00,
            user=self.user
        )
        recp2.ingredients.add(ing)

        res = self.client.get(INGR_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
