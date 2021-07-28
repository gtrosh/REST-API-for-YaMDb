from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator
from rest_framework import serializers

from .models import Category, Comment, Genre, Review, Title

User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field="username"
    )
    review = serializers.SlugRelatedField(read_only=True, slug_field="id")
    title = serializers.SlugRelatedField(read_only=True, slug_field="id")

    class Meta:
        model = Comment
        fields = ("id", "text", "author", "pub_date", "review", "title")


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=False,
        slug_field="username",
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        model = Review
        fields = ("id", "text", "author", "score", "pub_date")


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name", "slug"]


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["name", "slug"]


class TitleGetSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(
        many=True,
        read_only=True,
    )
    category = CategorySerializer(read_only=True)

    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = "__all__"


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field="slug", queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field="slug", queryset=Genre.objects.all(), many=True
    )

    class Meta:
        fields = "__all__"
        model = Title


class ConfirmationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(allow_blank=False, required=True)

    class Meta:
        validators = [EmailValidator]


class ActivationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(allow_blank=False, required=True)
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "bio",
            "email",
            "role",
        )
