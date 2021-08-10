import json

from django.db.models import Count, Q
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework import authentication
from rest_framework import viewsets, permissions, status

from recipes_app.models import Recipe, Ingredient
from recipes_app.permissions import IsOwnerOrReadOnly, IsNotOwner
from recipes_app.serializers import RecipeSerializer, IngredientSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def create(self, request, *args, **kwargs):
        data = request.data
        ingredients = data.pop("ingredients")
        recipe = Recipe.objects.create(owner=request.user, **data)
        for ingredient in ingredients:
            recipe.ingredients.add(ingredient)
        recipe.save()
        rs = RecipeSerializer(recipe, read_only=True)
        return JsonResponse(data=rs.data, status=status.HTTP_201_CREATED)


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class MostUsedIngredientsViewSet(generics.ListAPIView):
    serializer_class = IngredientSerializer

    def get_queryset(self):
        queryset = Ingredient.objects.annotate(recipe_count=Count('recipe')).order_by('-recipe_count')[:5]
        return queryset


class OwnRecipesViewSet(generics.ListAPIView):
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        recipes = Recipe.objects.filter(owner=user)
        return recipes


class RateRecipeViewSet(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated, IsNotOwner)
    queryset = Recipe.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            recipe_id = int(self.request.query_params.get('recipe', None))
            rating = int(json.loads(request.body).get('rating', None))
        except ValueError:
            return JsonResponse(data={'message': 'Wrong type of id or rating.'}, status=status.HTTP_400_BAD_REQUEST)
        except TypeError:
            return JsonResponse(data={'message': 'Recipe id or rating malformed.'}, status=status.HTTP_400_BAD_REQUEST)

        if rating is None:
            return JsonResponse(data={'message': 'Rating is missing'}, status=status.HTTP_400_BAD_REQUEST)

        if 0 < rating < 6:
            recipe = Recipe.objects.filter(id=recipe_id)
            if recipe:
                recipe = recipe.first()
                self.check_object_permissions(request, recipe)
                recipe.number_of_ratings += 1
                recipe.rating = (recipe.rating or 0) * recipe.number_of_ratings - (float(recipe.rating or 0) - float(rating))
                recipe.save()
                return JsonResponse(data={"message": "Recipe rated successfully."}, status=status.HTTP_200_OK)
            return JsonResponse(data={"message": "Recipe not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return JsonResponse(data={"message": "Invalid rating value."},
                                status=status.HTTP_400_BAD_REQUEST, )


class RecipeSearchViewSet(generics.ListAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend]
    search_fields = ['name', 'text', 'ingredients']


class RecipeFilterViewSet(generics.ListAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        try:
            number_of_max = int(self.request.query_params.get('max', None))
            number_of_min = int(self.request.query_params.get('min', None))
        except ValueError:
            return JsonResponse(data={'message': 'Wrong type of parameters.'}, status=status.HTTP_400_BAD_REQUEST)
        except TypeError:
            return JsonResponse(data={'message': 'Parameters malformed.'}, status=status.HTTP_400_BAD_REQUEST)

        if number_of_max and number_of_max > 0:
            queryset = Recipe.objects.annotate(ingredient_count=Count('ingredients')).order_by('-ingredient_count')[:number_of_max]
            return queryset
        elif number_of_min and number_of_min > 0:
            queryset = Ingredient.objects.annotate(recipe_count=Count('recipe')).order_by('recipe_count')[:number_of_min]
            return queryset

        return Recipe.objects.none()
