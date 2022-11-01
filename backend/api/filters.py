from rest_framework.exceptions import NotAuthenticated
from django_filters.rest_framework import filters, FilterSet

from recipes.models import Recipe
from users.models import User

class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.ModelChoiceFilter(queryset=User.objects.all())

    class Meta:
        model = Recipe
        fields = ['author__id', 'tags']

    def filter_is_favorited(self, queryset, field_name, value):
        user = self.request.user
        if user.is_anonymous:
            raise NotAuthenticated(
                'Войдите или зарегистрируйтесь, чтобы просматривать избранное.'
            )
        if value:
           return queryset.filter(favorited__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, field_name, value):
        user = self.request.user
        if user.is_anonymous:
            raise NotAuthenticated(
                'Войдите или зарегистрируйтесь, чтобы просматривать '
                'свой список покупок.'
            )
        if value:
           return queryset.filter(shoppingcart__user=user)
        return queryset


class SubscriptionsFilter(FilterSet):
    recipes_limit = filters.NumberFilter(
        field_name='recipes_limit', 
        method='paginate_recipes',
    )

    def paginate_recipes(self, queryset, field_name, value):
        if self.request.user.is_authenticated and value:
            queryset = queryset.filter(
                following__user=self.request.user
            ).values('recipes')[:value]
        return queryset

    class Meta:
        model = Recipe
        fields = ['recipes_limit',] 
