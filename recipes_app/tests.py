import json

from rest_framework import status
import pytest
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate, APIClient

from recipes_app.models import UserProfile, Recipe, Ingredient
from recipes_app.viewsets import RecipeViewSet, IngredientsViewSet

REGISTER_URL = '/profile/register/'
LOGIN_URL = '/profile/login/'
RECIPES_URL = '/recipes/'
INGREDIENTS_URL = '/ingredients/'
MOST_USED_INGREDIENTS_URL = '/most-used-ingredients/'
RATE_RECIPES_URL = '/recipes/rate/'
RECIPES_OWN_URL = '/recipes-own/'
RECIPES_SEARCH_URL = '/recipes-search/'
RECIPES_FILTER_URL = '/recipes-filter/'


class UserProfileTests(APITestCase):
    def test_register(self):
        data = {
            'first_name': 'test_name',
            'last_name': 'test_last_name',
            'username': 'test_username',
            'email': 'test_email@mail.com',
            'password1': 'testtest123123',
            'password2': 'testtest123123'
        }
        response = self.client.post(REGISTER_URL, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertEqual(UserProfile.objects.get().username, 'test_username')
        self.assertEqual(UserProfile.objects.get().last_name, 'test_last_name')
        self.assertEqual(UserProfile.objects.get().first_name, 'test_name')
        self.assertEqual(UserProfile.objects.get().email, 'test_email@mail.com')

    def test_login(self):
        register_data = {
            'first_name': 'test_name',
            'last_name': 'test_last_name',
            'username': 'test_username',
            'email': 'test_email@mail.com',
            'password1': 'testtest123123',
            'password2': 'testtest123123'
        }
        login_data = {
            'username': 'test_username',
            'password': 'testtest123123'
        }
        _ = self.client.post(REGISTER_URL, register_data, format='json')
        response = self.client.post(LOGIN_URL, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RecipeTest(APITestCase):
    def setUp(self):
        register_data = {
            'first_name': 'test_name',
            'last_name': 'test_last_name',
            'username': 'test_username',
            'email': 'test_email@mail.com',
            'password1': 'testtest123123',
            'password2': 'testtest123123'
        }
        _ = self.client.post(REGISTER_URL, register_data, format='json')
        self.factory = APIRequestFactory()
        self.create_view = RecipeViewSet.as_view({'post': 'create'})
        self.get_view = RecipeViewSet.as_view({'get': 'retrieve'})
        self.list_view = RecipeViewSet.as_view({'get': 'list'})
        self.delete_view = RecipeViewSet.as_view({'delete': 'destroy'})
        self.update_view = RecipeViewSet.as_view({'patch': 'update'})
        self.create_ingredient_view = IngredientsViewSet.as_view({'post': 'create'})
        self.user = UserProfile.objects.get(username='test_username')
        request = self.factory.post('/ingredients/', data={"name_of_the_ingredient": "chilli"})
        force_authenticate(request, user=self.user)
        self.create_ingredient_view(request)
        recipe = Recipe.objects.create(
            id=2,
            owner=self.user,
            recipe_text="text",
            name_of_the_recipe="some name",
        )
        recipe.ingredients.add(Ingredient.objects.get())
        user = UserProfile.objects.create(username='test', last_name='test', first_name='test', email='test@test.com')
        Recipe.objects.create(recipe_text='random', name_of_the_recipe='rand', owner_id=user.id)

    def test_recipe_creation(self):
        recipe_data = {
            'recipe_text': 'test_text',
            'name_of_the_recipe': 'test_name',
            'ingredients': '1'
        }
        request = self.factory.post(RECIPES_URL, data=recipe_data, format='json')
        force_authenticate(request, user=self.user)
        response = self.create_view(request)
        recipe_count = Recipe.objects.count()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(recipe_count, 3)

    def test_recipe_get(self):
        request = self.factory.get(RECIPES_URL)
        force_authenticate(request, user=self.user)
        response = self.get_view(request, pk=2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_recipe_update(self):
        recipe_data = {
            'name_of_the_recipe': 'new_name',
            'recipe_text': 'new_text',
            'ingredients': []
        }
        request = self.factory.patch(RECIPES_URL, data=recipe_data)
        force_authenticate(request, user=self.user)
        response = self.update_view(request, pk=2)
        recipe = Recipe.objects.get(pk=2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.recipe_text, 'new_text')
        self.assertEqual(recipe.name_of_the_recipe, 'new_name')

    def test_recipe_get_all(self):
        request = self.factory.get(RECIPES_URL)
        force_authenticate(request, user=self.user)
        response = self.list_view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_recipe_get_own(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.get(RECIPES_OWN_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_recipe_rate(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        correct_rating = {'rating': 4}
        under_correct_rating = {'rating': '-1'}
        above_correct_rating = {'rating': '7'}
        forbidden_response = client.post(RATE_RECIPES_URL + '?recipe=2', data=correct_rating, format='json')
        under_correct_response = client.post(RATE_RECIPES_URL + '?recipe=3', data=under_correct_rating, format='json')
        above_correct_response = client.post(RATE_RECIPES_URL + '?recipe=3', data=above_correct_rating, format='json')
        correct_response = client.post(RATE_RECIPES_URL + '?recipe=3', data=correct_rating, format='json')
        self.assertEqual(forbidden_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(under_correct_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(above_correct_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(correct_response.status_code, status.HTTP_200_OK)

    def test_recipe_delete(self):
        request = self.factory.delete(RECIPES_URL)
        force_authenticate(request, user=self.user)
        response = self.delete_view(request, pk=2)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_recipe_filter(self):
        ing1 = Ingredient.objects.create(name_of_the_ingredient='carrot')
        ing2 = Ingredient.objects.create(name_of_the_ingredient='cabbage')
        ing3 = Ingredient.objects.create(name_of_the_ingredient='apple')
        ing4 = Ingredient.objects.create(name_of_the_ingredient='beans')
        most_ingredients_recipe = Recipe.objects.create(
            id=122,
            owner=self.user,
            recipe_text="text",
            name_of_the_recipe="some name",
        )
        least_ingredients_recipe = Recipe.objects.create(
            id=5,
            owner=self.user,
            recipe_text="text",
            name_of_the_recipe="some name",
        )
        Recipe.objects.create(
            id=7,
            owner=self.user,
            recipe_text="text",
            name_of_the_recipe="some name",
        ).ingredients.add(ing3)
        Recipe.objects.create(
            id=8,
            owner=self.user,
            recipe_text="text",
            name_of_the_recipe="some name",
        ).ingredients.add(ing2)
        most_ingredients_recipe.ingredients.add(ing1)
        most_ingredients_recipe.ingredients.add(ing2)
        most_ingredients_recipe.ingredients.add(ing3)
        most_ingredients_recipe.ingredients.add(ing4)
        print((self.client.get(RECIPES_FILTER_URL + '?max=1')))

    def test_recipe_search(self):
        pass


class IngredientTest(APITestCase):
    def setUp(self):
        register_data = {
            'first_name': 'test_name',
            'last_name': 'test_last_name',
            'username': 'test_username',
            'email': 'test_email@mail.com',
            'password1': 'testtest123123',
            'password2': 'testtest123123'
        }
        _ = self.client.post(REGISTER_URL, register_data, format='json')
        self.user = UserProfile.objects.get(username='test_username')
        self.create_view = IngredientsViewSet.as_view({'post': 'create'})
        self.get_view = IngredientsViewSet.as_view({'get': 'retrieve'})
        self.delete_view = IngredientsViewSet.as_view({'delete': 'destroy'})
        self.update_view = IngredientsViewSet.as_view({'patch': 'update'})
        self.factory = APIRequestFactory()
        Ingredient.objects.create(name_of_the_ingredient='carrot')

    def test_ingredient_creation(self):
        ingredient_data = {
            'name_of_the_ingredient': 'tomato'
        }
        request = self.factory.post(INGREDIENTS_URL, data=ingredient_data, format='json')
        force_authenticate(request, user=self.user)
        response = self.create_view(request)
        recipe_count = Ingredient.objects.count()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(recipe_count, 2)

    def test_ingredient_get(self):
        request = self.factory.get(INGREDIENTS_URL)
        force_authenticate(request, user=self.user)
        response = self.get_view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_ingredient_update(self):
        ingredient_data = {
            'name_of_the_ingredient': 'new_name',
        }
        request = self.factory.patch(INGREDIENTS_URL, data=ingredient_data)
        force_authenticate(request, user=self.user)
        response = self.update_view(request, pk=1)
        ingredient = Ingredient.objects.get(pk=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredient.name_of_the_ingredient, 'new_name')

    def test_get_most_used_ingredients(self):
        ing1 = Ingredient.objects.create(name_of_the_ingredient='carrot')
        ing2 = Ingredient.objects.create(name_of_the_ingredient='cabbage')
        ing3 = Ingredient.objects.create(name_of_the_ingredient='apple')
        ing4 = Ingredient.objects.create(name_of_the_ingredient='beans')
        most_ingredients_recipe = Recipe.objects.create(
            id=2,
            owner=self.user,
            recipe_text="text",
            name_of_the_recipe="some name",
        )
        least_ingredients_recipe = Recipe.objects.create(
            id=3,
            owner=self.user,
            recipe_text="text",
            name_of_the_recipe="some name",
        )
        Recipe.objects.create(
            id=4,
            owner=self.user,
            recipe_text="text",
            name_of_the_recipe="some name",
        ).ingredients.add(ing3)
        Recipe.objects.create(
            id=5,
            owner=self.user,
            recipe_text="text",
            name_of_the_recipe="some name",
        ).ingredients.add(ing2)
        most_ingredients_recipe.ingredients.add(ing1)
        most_ingredients_recipe.ingredients.add(ing2)
        most_ingredients_recipe.ingredients.add(ing3)
        most_ingredients_recipe.ingredients.add(ing4)
        response = self.client.get(MOST_USED_INGREDIENTS_URL)
        self.assertEqual(json.loads(response.content)[0]['name_of_the_ingredient'], 'cabbage')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 5)

    def test_ingredient_delete(self):
        request = self.factory.delete(INGREDIENTS_URL)
        force_authenticate(request, user=self.user)
        response = self.delete_view(request, pk=1)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
