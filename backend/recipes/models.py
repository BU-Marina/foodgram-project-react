from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Название',
        help_text='Дайте название рецепту'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Опишите своё блюдо'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Обложка',
        help_text='Загрузите фото результата'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        help_text='Введите время необходимое для приготовления в минутах'
    )

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Ингредиент',
        help_text='Введите название'
    )


class RecipesIngredients(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients'
    )
    ingredient = models.ForeignKey(               # Должно выбираться из списка (с возможностью добавить новый)
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        help_text='Укажите количество'
    )
    measure_unit = models.CharField(              # Должно выбираться из списка (без возможности добавить новый)
        max_length=...,
        verbose_name='Единица измерения',
        help_text='Выберите единицу измерения'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'], name='unique_recipe_ingredient')
        ]


class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Тег',
        help_text=...
    )
    slug = models.SlugField(
        unique=True,
        verbose_name=...
    )
    color = models.CharField(
        max_length=6,
        verbose_name='Цвет'
    )


class RecipesTags(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='tags'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='recipes'
    )        # Должно выбираться из списка

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'], name='unique_recipe_tag')
        ]


class UsersFavourites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favourites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='followers'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favourite')
        ]
