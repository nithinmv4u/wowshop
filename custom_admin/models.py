from django.db import models

# Create your models here.
class UserProfile(models.Model):
    # username = models.CharField(max_length = 70)
    first_name = models.CharField(max_length = 70)
    last_name = models.CharField(max_length = 70)
    username=models.EmailField(max_length=240)
    password = models.CharField(max_length = 100)
    Confirm_password = models.CharField(max_length = 100)