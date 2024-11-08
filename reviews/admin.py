from django.contrib import admin
from .models import Review, Category, Genre

# Registers the Review model in the admin interface with custom display options
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'author_director', 'genre', 'rating', 'created_at', 'user', 'img')  # Fields displayed in the list view
    search_fields = ('title', 'author_director', 'genre')  # Enables search functionality on specific fields

# Registers the Category model in the admin interface with basic configurations
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Displays only the name field in the list view
    search_fields = ('name',)  # Allows searching by name in the admin interface

# Registers the Genre model in the admin interface with additional filter options
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')  # Displays name and associated category in the list view
    search_fields = ('name',)  # Enables search by genre name
    list_filter = ('category',)  # Adds a filter option by category in the admin interface
