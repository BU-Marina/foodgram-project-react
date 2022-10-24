from django.contrib import admin
from .models import (
    Recipe, Ingredient, RecipesIngredients, Tag, RecipesTags,
    UsersFavourites
)

admin.register(Recipe)
admin.register(Ingredient)
admin.register(RecipesIngredients)
admin.register(Tag)
admin.register(RecipesTags)
admin.register(UsersFavourites)
