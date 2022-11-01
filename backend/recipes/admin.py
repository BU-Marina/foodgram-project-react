from django.contrib import admin
from .models import (
    Recipe, Ingredient, RecipeIngredient, Tag, RecipeTag,
    Favorite
)

admin.site.register(Recipe)
admin.site.register(Ingredient)
admin.site.register(RecipeIngredient)
admin.site.register(Tag)
admin.site.register(RecipeTag)
admin.site.register(Favorite)
