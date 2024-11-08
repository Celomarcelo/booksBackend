from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

# Signal receiver to automatically create a Profile when a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:  # Checks if a new User instance was created
        Profile.objects.create(user=instance)  # Creates a Profile linked to the new User

# Signal receiver to save the Profile whenever the User is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()  # Ensures the linked Profile is saved whenever the User instance is saved
