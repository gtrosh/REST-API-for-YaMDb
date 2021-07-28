from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["id"]


class Genre(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название жанра")
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["id"]


class Title(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    year = models.SmallIntegerField(verbose_name="Год создания")
    description = models.TextField(verbose_name="Описание", null=True)
    genre = models.ManyToManyField(
        Genre, related_name="titles", verbose_name="Жанр"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="titles",
        verbose_name="Категория",
        null=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["id"]


class Review(models.Model):

    score = models.PositiveSmallIntegerField(
        verbose_name="оценка",
        blank=False,
        validators=[
            MinValueValidator(
                limit_value=1, message="Укажите значение не ниже - 1"
            ),
            MaxValueValidator(
                limit_value=10, message="Укажите значение не выше - 10"
            ),
        ],
    )
    text = models.TextField(blank=True, null=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews"
    )
    title = models.ForeignKey(
        Title,
        verbose_name="произведение",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    pub_date = models.DateTimeField(
        verbose_name="дата добавления", auto_now_add=True
    )

    class Meta:
        ordering = ["-pub_date"]
        # unique_together = ['author', 'title']

    def __str__(self):
        return f"{self.author} оставил отзыв на '{self.title}'"


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name="comments"
    )
    pub_date = models.DateTimeField(
        verbose_name="дата добавления", auto_now_add=True
    )

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.text[:20]
