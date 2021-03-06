"""recipes_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from rest_framework import routers
from recipes_app import viewsets
from django.urls import path, include


recipes_router = routers.SimpleRouter()
recipes_router.register(r'recipes', viewsets.RecipeViewSet)
recipes_router.register(r'ingredients', viewsets.IngredientsViewSet, basename='ingredients')


urlpatterns = [
    # path('admin/', admin.site.urls),
    path('profile/register/', include('dj_rest_auth.registration.urls')),
    path('profile/', include('dj_rest_auth.urls')),
    path(r'most-used-ingredients/', viewsets.MostUsedIngredientsViewSet.as_view(), name='most-used-ingredients'),
    path(r'recipes/rate/', viewsets.RateRecipeViewSet.as_view(), name='rate-recipes'),
    path(r'recipes-own/', viewsets.OwnRecipesViewSet.as_view(), name='recipes-own'),
    path(r'recipes-search/', viewsets.RecipeSearchViewSet.as_view(), name='recipes-search'),
    path(r'recipes-filter/', viewsets.RecipeFilterViewSet.as_view(), name='recipes-filter'),
    path('', include(recipes_router.urls)),
]

