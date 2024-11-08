from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework import viewsets, generics, status
from .models import Review, Category, Genre, Like, Comment
from .serializers import ReviewSerializer, UserSerializer, UserFavoriteSerializer, CategorySerializer, GenreSerializer, LikeSerializer, CommentSerializer
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


def frontend(request):
    return render(request, 'index.html')


# Custom serializer for JWT token, adding additional user details
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['username'] = user.username
        token['id'] = user.id

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Adds user info to the token response
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
        }

        return data


# Custom JWT token view using the CustomTokenObtainPairSerializer
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ViewSet for managing Review objects in the API
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('genre__category').all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]


# API view to register a new user
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        # Validates required fields
        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Checks for unique username and email
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # Creates user and returns JWT tokens
        try:
            user = User(username=username, email=email)
            user.set_password(password)
            user.save()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


# View to retrieve or update user profile
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def user_profile(request):
    user = request.user

    if request.method == 'GET':
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data, context={
                                    'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# View to handle password change
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        user = request.user

        # Checks if the current password is correct
        if not user.check_password(current_password):
            return Response({"error": "Current password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)


# API view to create a new review
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_review(request):
    if request.method == 'POST':
        serializer = ReviewSerializer(
            data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        print(serializer.errors)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# API view to retrieve the reviews created by the authenticated user
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_reviews(request):
    user = request.user
    reviews = Review.objects.filter(user=user)
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)


# API view to edit a specific review by its ID
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def edit_review(request, reviewId):
    parser_classes = [MultiPartParser, FormParser]
    try:

        review = Review.objects.get(id=reviewId, user=request.user)
    except Review.DoesNotExist:
        return JsonResponse({'error': 'Review not found.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ReviewSerializer(review, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)

    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# API view to delete a specific review by its ID
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_review(request, reviewId):
    try:
        review = Review.objects.get(id=reviewId, user=request.user)
    except Review.DoesNotExist:
        return JsonResponse({'error': 'Review not found.'}, status=status.HTTP_404_NOT_FOUND)

    review.delete()
    return JsonResponse({'message': 'Review deleted successfully.'}, status=status.HTTP_200_OK)


# API view to retrieve a list of reviews created by a specific user
@permission_classes([IsAuthenticated])
class UserReviewsView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        user_id = self.kwargs['user_id']
        return Review.objects.filter(user__id=user_id)


# API view to retrieve detailed information about a specific user by their ID
class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=404)

        serializer = self.get_serializer(user)
        return Response(serializer.data)


# API view to toggle favorite status for a specific user
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, user_id):
    user = request.user
    try:
        favorite_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    if favorite_user in user.profile.favorites.all():
        user.profile.favorites.remove(favorite_user)
        return Response({'message': f'{favorite_user.username} removed from favorites.'})
    else:
        user.profile.favorites.add(favorite_user)
        return Response({'message': f'{favorite_user.username} added to favorites.'})


# API view to list all favorite users for the authenticated user
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_favorites(request):
    user = request.user
    favorites = user.profile.favorites.all()
    serializer = UserFavoriteSerializer(favorites, many=True)
    return Response(serializer.data)


# API view to retrieve details of a specific review by its ID
@api_view(['GET'])
def review_detail(request, review_id):
    try:
        review = Review.objects.get(id=review_id)
    except Review.DoesNotExist:
        return Response({'error': 'Review not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ReviewSerializer(review)
    return Response(serializer.data)


# API view to list all categories
@api_view(['GET'])
def list_categories(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


# API view to retrieve genres within a specific category
@api_view(['GET'])
def list_genres(request):
    genres = Genre.objects.all()
    serializer = GenreSerializer(genres, many=True)
    return Response(serializer.data)


# API view to filter reviews by category or genre
@api_view(['GET'])
def category_genres(request, id):
    try:
        category = Category.objects.get(pk=id)
    except Category.DoesNotExist:
        return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    genres = Genre.objects.filter(category=category)
    serializer = GenreSerializer(genres, many=True)
    return Response(serializer.data)


# API view to search for reviews by title, author, or content
@api_view(['GET'])
def filtered_reviews(request):
    category_id = request.query_params.get('category', None)
    genre_id = request.query_params.get('genre', None)

    reviews = Review.objects.all()

    if category_id:
        reviews = reviews.filter(genre__category_id=category_id)
    if genre_id:
        reviews = reviews.filter(genre_id=genre_id)

    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)


# API view to search for reviews by title, author, or content
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_reviews(request):
    query = request.query_params.get('q', None)
    if not query:
        return Response({"error": "Search query is required"}, status=400)

    reviews = Review.objects.filter(
        Q(title__icontains=query) |
        Q(author_director__icontains=query) |
        Q(content__icontains=query)
    )

    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data, status=200)


# API view to like or unlike a review
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_review(request, review_id):
    review = Review.objects.get(id=review_id)
    like, created = Like.objects.get_or_create(
        review=review, user=request.user)
    if not created:
        like.delete()
        return Response({
            'message': 'Like removed',
            'likes': review.likes.count()
        }, status=status.HTTP_200_OK)
    return Response({
        'message': 'Review liked',
        'likes': review.likes.count()
    }, status=status.HTTP_201_CREATED)


# API view to add a comment to a review
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment(request, review_id):
    content = request.data.get('content')

    if not content:
        return Response({"error": "Content field is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        review = Review.objects.get(id=review_id)
        comment = Comment.objects.create(
            user=request.user, review=review, content=content)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except Review.DoesNotExist:
        return Response({"error": "Review not found."}, status=status.HTTP_404_NOT_FOUND)


# API view to list all comments for a specific review
@api_view(['GET'])
def list_comments(request, review_id):
    review = Review.objects.get(id=review_id)
    comments = review.comments.all()
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)


# API view to delete a specific comment by its ID
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment(request, comment_id):
    try:
        comment = Comment.objects.get(id=comment_id, user=request.user)
    except Comment.DoesNotExist:
        return Response({"error": "Comment not found or you don't have permission to delete this comment."}, status=status.HTTP_404_NOT_FOUND)

    comment.delete()
    return Response({"message": "Comment deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
