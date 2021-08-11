from django.db import models
from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser):
    first_name = models.CharField(max_length=150, blank=False)
    last_name = models.CharField(max_length=150, blank=False)
    email = models.EmailField(max_length=150, blank=False)
    location = models.CharField(max_length=250, blank=True, null=True)
    time_zone = models.CharField(max_length=250, blank=True, null=True)
    city = models.CharField(max_length=150, blank=True, null=True)
    employment = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return f'{self.username} - {self.email}'


class Ingredient(models.Model):
    name_of_the_ingredient = models.CharField(max_length=250, blank=False)

    def __str__(self):
        return f'{self.name_of_the_ingredient}'


class Recipe(models.Model):
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(Ingredient, blank=True)
    recipe_text = models.TextField(blank=False)
    name_of_the_recipe = models.CharField(max_length=250, blank=False)
    number_of_ratings = models.PositiveIntegerField(default=0, blank=True)
    rating = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f'{self.name_of_the_recipe} - {self.rating}'
