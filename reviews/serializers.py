from rest_framework import serializers
from .models import Review, Profile, Genre, Category, Like, Comment
from django.contrib.auth.models import User

# Serializer for User model, adding fields from associated Profile model
class UserSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(
        source='profile.image', allow_null=True, required=False)  # Allows optional profile image from Profile model
    biography = serializers.CharField(
        source='profile.biography', allow_blank=True, required=False)  # Optional biography field from Profile model

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'profile_image', 'biography', 'id', 'is_superuser']  # Fields included in serialization

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', None)  # Extracts profile data if available
        instance.first_name = validated_data.get('first_name', instance.first_name)  # Updates first name if provided
        instance.last_name = validated_data.get('last_name', instance.last_name)  # Updates last name if provided
        instance.email = validated_data.get('email', instance.email)  # Updates email if provided
        instance.save()

        # Updates or creates associated Profile object if profile data is provided
        if profile_data:
            profile, created = Profile.objects.get_or_create(user=instance)
            profile.image = profile_data.get('image', profile.image)
            profile.biography = profile_data.get('biography', profile.biography)
            profile.save()

        return instance

# Serializer for Genre model
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name',]  # Fields included

# Serializer for Category model, including related genres
class CategorySerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)  # Nested serializer for genres, read-only

    class Meta:
        model = Category
        fields = ['id', 'name', 'genres']  # Fields included

# Serializer for Profile model with image and biography fields
class ProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(
        source='profile.image', allow_null=True, required=False)
    biography = serializers.CharField(required=False)

    class Meta:
        model = Profile
        fields = ['profile_image', 'biography']  # Fields included

# Serializer for User's favorite items with profile details
class UserFavoriteSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(
        source='profile.image', allow_null=True)  # Optional profile image from Profile model

    class Meta:
        model = User
        fields = ['id', 'username', 'profile', 'profile_image']  # Fields included

# Serializer for Like model
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'review', 'created_at']  # Fields included

# Serializer for Comment model with user details
class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')  # Read-only username from related User model
    user_id = serializers.ReadOnlyField(source='user.id')  # Read-only user ID from related User model

    class Meta:
        model = Comment
        fields = ['id', 'user_id', 'user_name', 'review', 'content', 'created_at']  # Fields included

# Serializer for Review model with related data
class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Nested serializer for User, read-only
    genre = serializers.PrimaryKeyRelatedField(queryset=Genre.objects.all())  # Genre relation by primary key
    genre_name = serializers.SerializerMethodField()  # Retrieves genre name
    category_id = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)  # Nested comments, read-only
    likes = serializers.IntegerField(source='likes_count', read_only=True)  # Count of likes

    class Meta:
        model = Review
        fields = ['id', 'title', 'author_director', 'genre', 'genre_name',
                  'rating', 'content', 'img', 'created_at', 'user', 'comments', 'likes', 'category_id']  # Fields included

    def get_genre_name(self, obj):
        return obj.genre.name  # Retrieves the genre name for the review
    
    def get_category_id(self, obj):
        return obj.genre.category.id if obj.genre and obj.genre.category else None  # Retrieves category ID

    def create(self, validated_data):
        user = self.context['request'].user  # Gets the user from the request context
        validated_data.pop('user', None)  # Removes user from validated data to avoid duplicate assignment
        review = Review.objects.create(user=user, **validated_data)  # Creates the Review instance with the current user
        return review  # Returns the newly created review



