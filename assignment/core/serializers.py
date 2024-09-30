from rest_framework import serializers
from .models import App, Task
from django.contrib.auth.models import User
from .models import UserProfile

class AppSerializer(serializers.ModelSerializer):
    class Meta:  
        model = App
        fields = ['id', 'name', 'link', 'category', 'sub_category', 'points', 'image'] 
        # read_only_fields = ['user']

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['user','app', 'screenshot', 'completed']

class AdminTaskReviewSerializer(serializers.ModelSerializer):
    app_name = serializers.CharField(source='app.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'app_name', 'user_name', 'screenshot', 'completed']
