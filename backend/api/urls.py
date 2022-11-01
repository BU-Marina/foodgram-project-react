from django.urls import include, path
from rest_framework import routers

from .views import (RecipeViewSet, TagViewSet, IngredientViewSet,
                    CustomUserViewSet)

router = routers.DefaultRouter()

router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
    # path('', include('djoser.urls')),
]
