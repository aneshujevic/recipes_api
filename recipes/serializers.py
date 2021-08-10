from abc import ABC

from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer

from recipes.models import Recipe, Ingredient


class RecipeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'


class IngredientSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RegistrationSerializer(RegisterSerializer):

    def update(self, instance, validated_data):
        return super().update(instance,validated_data)

    def create(self, validated_data):
        # TODO: Check via hunter if email exists else raise validation error
        return super().create(validated_data)

    def save(self, request):
        return super().save(request)
