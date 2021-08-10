from django.db.models import Count
from rest_framework import viewsets, permissions, status
from rest_framework import generics
from rest_framework.response import Response

from recipes_app.models import Recipe, Ingredient
from recipes_app.permissions import IsOwnerOrReadOnly, IsNotOwner, IsOwner
from recipes_app.serializers import RecipeSerializer, IngredientSerializer


class RecipesViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def create(self, request, *args, **kwargs):
        data = request.data
        ingredients = data.pop("ingredients")
        recipe = Recipe.objects.create(owner=request.user, **data)
        # recipe.save()
        for ingredient in ingredients:
            recipe.ingredients.add(ingredient)
        recipe.save()
        rs = RecipeSerializer(recipe, read_only=True)
        return Response(data=rs.data, status=status.HTTP_201_CREATED)


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
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    #
    def get_queryset(self):
        user = self.request.user
        return Recipe.objects.filter(owner=user)


class RateRecipeViewSet(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsNotOwner]
    lookup_url_kwarg = "recipe"

    def post(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get(self.lookup_url_kwarg)
        rating = request.POST.get('rating', None)
        if recipe_id is not None and rating is not None and isinstance(rating, int) and 0 < rating < 6:
            recipe = Recipe.objects.filter(id=recipe_id)
            if recipe is not None:
                recipe = recipe.first()
                recipe.number_of_ratings += 1
                recipe.rating = (recipe.rating + float(rating)) / float(recipe.number_of_ratings)
                recipe.save()
                return Response(data='{"message": "Recipe rated successfully."}', status=status.HTTP_200_OK)
            return Response(data='{"message": "Recipe not found."}', status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(data='{"message": "Bad request."}', status=status.HTTP_400_BAD_REQUEST)

