from django.db import models
from django.contrib.auth.models import User

class App(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    link = models.URLField()
    category = models.CharField(max_length=50)
    sub_category = models.CharField(max_length=50)
    image = models.ImageField(upload_to='apps/')
    points = models.IntegerField()

    def __str__(self):
        return self.name

class Task(models.Model):
    PENDING = 'P'
    SUCCESS = 'S'
    FAILURE = 'F'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SUCCESS, 'Success'),
        (FAILURE, 'Failure'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    app = models.ForeignKey(App, on_delete=models.CASCADE)
    screenshot = models.ImageField(upload_to='screenshots/')
    completed = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PENDING)

class UserProfile(models.Model):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    def __str__(self):
        return self.user.username

