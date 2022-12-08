from django.contrib.auth import get_user_model
from django.db import models
from django.core import validators


User = get_user_model()


class Ingredient(models.Model):
    title = models.CharField('Название', max_length=200)
    unit = models.CharField('Единица измерения', max_length=200)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор публикации',
    )

    image = models.ImageField(
        'Изображение',
        upload_to='recipes/'
    )
    name = models.CharField('Название', max_length=250)
    text = models.TextField('Описание')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='Ingredients_in_recipe',
        related_name='recipes',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[validators.MinValueValidator(
            1, message='Минимальное значение - 1 минута!'
        )]
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Tag(models.Model):

    name = models.CharField(
        'Название',
        max_length=60,
        unique=True)
    color_hex = models.CharField(
        'Цвет',
        max_length=7,
        unique=True)
    slug = models.SlugField(
        'Слаг',
        max_length=150,
        unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Тпги'
        ordering = ['-id']

    def __str__(self):
        return self.name


class Ingredients_quantity(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients_list',
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    quantity = models.PositiveSmallIntegerField(
        'Количество',
        validators=[validators.MinValueValidator(
            1, message='Минимальное значение - 1 ед.!'
            )])

    class Meta:
        verbose_name = 'кол-во ингредиента'
        verbose_name_plural = 'кол-во ингредиентов'

    def __str__(self):
        return f'Из рецепта "{self.recipe}"'
