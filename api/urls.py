from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ActivateUserViewSet,
    CategoryViewSet,
    CommentViewSet,
    GenreViewSet,
    ReviewViewSet,
    SendEmailConfirmationViewSet,
    TitleViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="categories")
router.register(r"genres", GenreViewSet, basename="genres")
router.register(r"titles", TitleViewSet, basename="titles")
router.register(r"users", UserViewSet, basename="users")
router.register(
    r"titles/(?P<title_id>\d+)/reviews", ReviewViewSet, basename="reviews"
)
router.register(
    r"titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments",
    CommentViewSet,
    basename="comments",
)

urlpatterns = [
    path("v1/", include(router.urls)),
    path(
        "v1/auth/email/",
        SendEmailConfirmationViewSet.as_view(),
        name="send_email_with_code",
    ),
    path(
        "v1/auth/token/",
        ActivateUserViewSet.as_view(),
        name="token_obtain_pair",
    ),
]
