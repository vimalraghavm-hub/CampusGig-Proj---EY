from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_freelancer = models.BooleanField(default=False)
    is_client = models.BooleanField(default=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    skills = models.CharField(max_length=255, blank=True, help_text="Comma separated skills")
    portfolio_url = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return self.username
