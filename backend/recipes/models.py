from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Ingredient(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name='Ингредиент',
        help_text='Введите название'
    )
    measurement_unit = models.CharField(              # Должно выбираться из списка (без возможности добавить новую е.и.*) choices
        max_length=50,
        verbose_name='Единица измерения',
        help_text='Выберите единицу измерения',
    )

    def __str__(self) -> str:
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Тег',
        help_text='Введите название тега'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг',
        help_text='Придумайте слаг тега'
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет',
        help_text='Введите введите hex-код цвета'
    )

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField( # Должно выбираться из списка (с возможностью добавить новый)
        Ingredient,
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField( # Должно выбираться из списка
        Tag,
        through='RecipeTag'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Дайте название рецепту'
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Опишите своё блюдо'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Обложка',
        help_text='Загрузите картинку готового блюда',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        help_text='Укажите время необходимое для приготовления (в минутах)'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество',
        help_text='Укажите количество'
    )


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'], name='unique_recipe_ingredient')
        ]

    def __str__(self) -> str:
        return f'Ингредиент {self.ingredient} используется в рецепте {self.recipe}'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'], name='unique_recipe_tag')
        ]

    def __str__(self) -> str:
        return f'У рецепта {self.recipe} есть тег {self.tag}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite')
        ]

    def __str__(self) -> str:
        return f'Рецепт {self.recipe} в избранном у {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shoppingcart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shoppingcart'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shoppingcart')
        ]

    def __str__(self) -> str:
        return f'Рецепт {self.recipe} в списке покупок у {self.user}'
