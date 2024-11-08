"""review_platform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from reviews.views import ReviewViewSet
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from reviews import views
from reviews.views import (
    CustomTokenObtainPairView, 
    RegisterView, 
    user_profile, 
    ChangePasswordView, 
    create_review, 
    user_reviews, 
    edit_review, 
    delete_review, 
    UserReviewsView, 
    UserDetailView, 
    toggle_favorite, 
    list_favorites, 
    review_detail,
    list_categories,
    list_genres,
    category_genres,
    filtered_reviews,
    search_reviews,
    like_review,
    list_comments,
    add_comment,
    delete_comment
)


router = DefaultRouter()
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/user/profile/', user_profile, name='user-profile'),
    path('user/change-password/',
         ChangePasswordView.as_view(), name='change-password'),
    path('reviews/create/', create_review, name='create_review'),
    path('reviews/user/', user_reviews, name='user-reviews'),
    path('reviews/<int:reviewId>/', edit_review, name='edit_review'),
    path('reviews/<int:reviewId>/delete/', delete_review, name='delete_review'),
    path('user/<int:user_id>/reviews/', UserReviewsView.as_view(), name='user-reviews'),
    path('user/<int:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('user/<int:user_id>/toggle-favorite/', toggle_favorite, name='toggle_favorite'),
    path('user/favorites/', list_favorites, name='user-favorites'),
    path('reviews-details/<int:review_id>/', review_detail, name='review_detail'),
    path('categories/', list_categories, name='list_categories'),
    path('genres/', list_genres, name='list_genres'),
    path('categories/<int:id>/genres/', category_genres, name='category-genres'),
    path('reviews/', filtered_reviews, name='filtered-reviews'),
    path('reviews/search/', search_reviews, name='search_reviews'),
    path('reviews/<int:review_id>/like/', like_review, name='like_review'),
    path('reviews/<int:review_id>/comments/', add_comment, name='add_comment'),
    path('reviews/<int:review_id>/comments/list/', list_comments, name='list_comments'),
    path('comments/<int:comment_id>/delete/', delete_comment, name='delete_comment'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    re_path(r'^(?:.*)/?$', views.frontend),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = TemplateView.as_view(template_name='index.html')
