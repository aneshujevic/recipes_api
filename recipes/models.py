from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User


class Ingredient(models.Model):
    name_of_ingredient = models.CharField(max_length=250, blank=False)

    def __str__(self):
        return f'{self.name_of_ingredient}'


class Recipe(models.Model):
    ingredients = models.ManyToManyField(Ingredient)
    recipe_text = models.TextField(blank=False)
    name_of_the_recipe = models.CharField(max_length=250, blank=False)
    rating = models.PositiveIntegerField(validators=[
        MaxValueValidator(5),
        MinValueValidator(1)
    ], blank=True)

    def __str__(self):
        return f'{self.name_of_the_recipe} - {self.rating}'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=250, blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.user.email}'
