from django.db import models
from django.contrib.auth.models import User

class Symbol(models.Model):
    name = models.CharField(max_length=5)
    
class UserWithFavorites(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorites = models.ManyToManyField(Symbol)