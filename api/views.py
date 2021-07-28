from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    filters,
    generics,
    mixins,
    serializers,
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.tokens import account_activation_token

from .filters import TitleFilter
from .models import Category, Comment, Genre, Review, Title
from .permissions import FullObjAccess, IsAdmin, ObjReadOnly, ReadOnly
from .serializers import (
    ActivationCodeSerializer,
    CategorySerializer,
    CommentSerializer,
    ConfirmationCodeSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleCreateSerializer,
    TitleGetSerializer,
    UserSerializer,
)

User = get_user_model()


class CreateDestroyListViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    pass


class CategoryViewSet(CreateDestroyListViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ReadOnly | IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["name"]
    search_fields = ["name"]
    lookup_field = "slug"


class GenreViewSet(CreateDestroyListViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [ReadOnly | IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["name"]
    search_fields = ["name"]
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg("reviews__score"))
    permission_classes = [ReadOnly | IsAdminUser]
    filter_backends = [
        DjangoFilterBackend,
    ]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ["create", "partial_update"]:
            return TitleCreateSerializer
        return TitleGetSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthenticated | ReadOnly,
        FullObjAccess | ObjReadOnly,
    ]

    def get_queryset(self, **kwargs):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get("review_id"),
            title=self.kwargs.get("title_id"),
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get("review_id"),
            title=self.kwargs.get("title_id"),
        )
        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthenticated | ReadOnly,
        FullObjAccess | ObjReadOnly,
    ]

    def get_queryset(self, **kwargs):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        if title.reviews.filter(author=self.request.user):
            raise serializers.ValidationError(
                "Вы не можете оставить еще один отзыв"
            )
        serializer.save(author=self.request.user, title=title)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def send_code_by_email(email, code):
    # send email with the  code
    email = EmailMessage(
        subject="your confirmation code",
        body=f"{code}",
        to=[email],
    )

    email.send()


class SendEmailConfirmationViewSet(generics.GenericAPIView):
    permission_classes = ()
    authentication_classes = ()

    serializer_class = ConfirmationCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        user_email = serializer.validated_data.get("email")

        # get or create user
        user, created = User.objects.get_or_create(
            email=user_email,
        )

        # check if user new or already was in the database
        if created:
            # create user without activation (
            # activate only after email is confrimed)
            user.is_active = False
            user.save(update_fields=["is_active"])

        # generate a code
        confirmation_code = account_activation_token.make_token(user)

        send_code_by_email(user_email, confirmation_code)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class ActivateUserViewSet(generics.GenericAPIView):
    permission_classes = ()
    authentication_classes = ()

    serializer_class = ActivationCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(
            User, email=serializer.validated_data.get("email")
        )

        if account_activation_token.check_token(
            user, serializer.validated_data.get("confirmation_code")
        ):
            user.is_active = True
            user.save()

            return Response(
                get_tokens_for_user(user), status=status.HTTP_200_OK
            )

        return Response(
            "token is not valid", status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = "username"

    permission_classes = [IsAuthenticated, IsAdmin]

    filter_backends = [filters.SearchFilter]
    search_fields = [
        "username",
    ]

    @action(
        detail=False,
        methods=["GET"],
        url_path="me",
        url_name="get_me",
        permission_classes=[IsAuthenticated],
    )
    def get_user_self(self, request, **kwargs):
        user = get_object_or_404(User, username=request.user.username)
        serializer = UserSerializer(instance=user)
        return Response(serializer.data)

    @get_user_self.mapping.patch
    def change_user_self(self, request, **kwargs):
        user = get_object_or_404(User, username=request.user.username)
        serializer = UserSerializer(
            instance=user, data=request.data, partial=True
        )
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    @get_user_self.mapping.delete
    def delete_user_self(self, request, **kwargs):
        """do not allow users to delete themselves"""
        return Response(
            {"error": "can not delete yourself"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )
