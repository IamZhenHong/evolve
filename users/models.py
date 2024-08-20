from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Add any custom fields here
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    social_media = models.URLField(blank=True, null=True)  
    
    
    # Other custom fields as needed