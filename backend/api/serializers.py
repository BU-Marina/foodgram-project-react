import base64
from django.shortcuts import get_object_or_404

# from django.contrib.auth import authenticate
# from django.db.models import Avg
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
# from rest_framework.exceptions import NotFound
# from rest_framework.validators import UniqueTogetherValidator
from recipes.models import (Recipe, Tag, Ingredient, RecipeIngredient,
                            RecipeTag, Favorite, ShoppingCart)
from users.models import Follow
from .pagination import LimitPagination

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'color', 'slug'
        )
        # read_only_fields = (
        #     'name', 'color', 'slug'
        # )


class UserSerializer(serializers.ModelSerializer):
    is_subscribe = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_subscribe'
        )

    def get_is_subscribe(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and Follow.objects.filter(user=user, following=obj).exists()
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        read_only=True, source='ingredient.id'
    )
    name = serializers.CharField(
        read_only=False, source='ingredient.name'
    )
    measurement_unit = serializers.CharField(
        read_only=False, source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')
        read_only_fields = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(
        many=True, read_only=False, source='recipe_ingredients'
    )
    # tags = TagSerializer(
    #     many=True, read_only=True
    # )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, read_only=False,
        queryset=Tag.objects.values_list('id', flat=True)
    )
    author = UserSerializer(many=False, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=True, read_only=False)

    class Meta:
        model = Recipe
        fields = (
            'id', 'ingredients', 'tags', 'author', 'image', 'name', 'text',
            'cooking_time', 'is_in_shopping_cart','is_favorited'
        )
        read_only_fields = (
            'id', 'author', 'is_favorited', 'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and Favorite.objects.filter(user=user, recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and ShoppingCart.objects.filter(user=user, recipe=obj).exists()
        )
    
    def create(self, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)

        for data in ingredients:
            amount = int(data.pop('amount'))
            ingredient = data['ingredient']
            current_ingredient, status = Ingredient.objects.get_or_create(
                **ingredient
            )
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=current_ingredient,
                amount=amount # , measurement_unit=measurement_unit
            )

        for tag_id in tags:
            current_tag = get_object_or_404(Tag, pk=tag_id)
            RecipeTag.objects.create(
                recipe=recipe, tag=current_tag
            )

        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)

        if 'recipe_ingredients' in validated_data:
            RecipeIngredient.objects.filter(
                recipe=instance
            ).delete()
            ingredients_data = validated_data.pop('recipe_ingredients')
            lst = []
            for data in ingredients_data:
                amount = int(data.pop('amount'))
                ingredient = data['ingredient']
                current_ingredient, status = Ingredient.objects.get_or_create(
                    **ingredient
                )
                RecipeIngredient.objects.create(
                    recipe=instance, ingredient=current_ingredient,
                    amount=amount
                )
                lst.append(current_ingredient)
            instance.ingredients.set(lst)

        if 'tags' in validated_data:
            tags_ids = validated_data.pop('tags')
            lst = []
            for tag_id in tags_ids:
                current_tag = get_object_or_404(Tag, pk=tag_id)
                lst.append(current_tag)
            instance.tags.set(lst)

        instance.save()
        return instance

    # def to_representation(self, instance):
    #     instance.tags.set(TagSerializer(instance.tags))
    #     return super().to_representation(instance)


class RecipeListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'image', 'cooking_time'
        )


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        read_only_fields = ('user', 'recipe',)
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Вы уже добавили этот рецепт в избранное'
            )
        ]

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id', 'username', 'password', 'email', 'first_name', 'last_name'
        )
        read_only_fields = ('id',)
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class SubscriptionsSerializer(serializers.ModelSerializer):
    recipes = RecipeListSerializer(many=True, read_only=True)
    # recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()
    is_subscribe = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribe', 'recipes', 'recipes_count'
        )

    # def get_recipes(self, obj):
    #     recipes = Recipe.objects.filter(author=obj)
    #     paginator = LimitPagination()
    #     print(recipes)
    #     page = paginator.paginate_queryset(recipes, self.context['request'])
    #     serializer = RecipeListSerializer(
    #         page, many=True, context={'request': self.context['request']}
    #     )
    #     print(serializer)
    #     return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_is_subscribe(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and Follow.objects.filter(user=user, following=obj).exists()
        )


class SubscribeSerializer(serializers.ModelSerializer):
    queryset = User.objects.all()
    user = serializers.PrimaryKeyRelatedField(queryset=queryset)
    following = serializers.PrimaryKeyRelatedField(queryset=queryset)

    class Meta:
        model = Follow
        fields = ('user', 'following')
        read_only_fields = ('user', 'following')
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following'),
                message='Вы уже подписаны на этого автора'
            )
        ]

    def validate_following(self, value):
        if self.context['request'].user == value:
            raise serializers.ValidationError(
                "Нельзя подписаться на самого себя"
            )
        return value

    def to_representation(self, instance):
        return SubscriptionsSerializer(
            instance.following,
            context={'request': self.context.get('request')}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        read_only_fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Вы уже добавили этот рецепт в список покупок'
            )
        ]

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
