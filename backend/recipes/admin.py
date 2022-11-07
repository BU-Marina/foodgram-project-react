from django.contrib import admin
from .models import (
    Recipe, Ingredient, RecipeIngredient, Tag, RecipeTag,
    Favorite, ShoppingCart
)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'pub_date')
    list_filter = ('name', 'author', 'tags')
    readonly_fields = ('favorited_by',)

    def favorited_by(self, obj):
        return obj.favorited.count()


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredient)
admin.site.register(Tag)
admin.site.register(RecipeTag)
admin.site.register(Favorite)
admin.site.register(ShoppingCart)
