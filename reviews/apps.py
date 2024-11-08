from django.apps import AppConfig

# Configuration class for the "reviews" application
class ReviewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # Sets the default type for auto-generated primary keys
    name = 'reviews'  # Defines the name of the application

    def ready(self):
        import reviews.signals  # Imports the signals module when the application is ready

