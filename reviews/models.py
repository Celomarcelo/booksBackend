from django.contrib.auth.models import User
from django.db import models

# Model representing a category of genres
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# Model representing a genre linked to a category
class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, related_name='genres', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

# Model representing a review, created by users and linked to a genre
class Review(models.Model):
    title = models.CharField(max_length=255)  # Title of the review
    author_director = models.CharField(max_length=255)  # Author or director of the reviewed content
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)  # Genre
    rating = models.IntegerField()  # Integer field to store the rating
    content = models.TextField()  # Main content
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of when the review was created
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')  # User who created the review
    img = models.ImageField(upload_to='reviews/', null=True, blank=True)  # Optional image associated with the review

    def __str__(self):
        return self.title

# Model representing a user profile with additional information
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # User model
    favorites = models.ManyToManyField(User, related_name='favorited_by', blank=True)  # Field for favorite users
    image = models.ImageField(upload_to='profile_images/', default='default.jpg')  # Profile image with a default setting
    biography = models.TextField(blank=True, null=True)  # Optional biography field for user profile

    def __str__(self):
        return self.user.username

# Model representing a like on a review by a user
class Like(models.Model):
    review = models.ForeignKey(Review, related_name='likes', on_delete=models.CASCADE)  # Link to the liked review
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who liked the review
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the like was created

    class Meta:
        unique_together = ('review', 'user')  # Ensures a user can like a review only once

# Model representing a comment on a review by a user
class Comment(models.Model):
    review = models.ForeignKey(Review, related_name='comments', on_delete=models.CASCADE)  # Link to the commented review
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who wrote the comment
    content = models.TextField()  # Content of the comment
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the comment was created
