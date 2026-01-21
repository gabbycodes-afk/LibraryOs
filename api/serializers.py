from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile, Book, ActivityLog
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["avatar"]

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email", "password", "profile"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "id", 
            "google_book_id", # This now holds the ISBN13
            "title", 
            "authors", 
            "description", 
            "image_url", 
            "preview_link", 
            "web_reader_link", # NEW: Added for the internal iframe
            "is_ebook",        # NEW: Added to tell React if it's readable
            "category", 
            "created_at"
        ]
        extra_kwargs = {"user": {"read_only": True}}

class ActivityLogSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(format="%b %d, %Y %H:%M", read_only=True)

    class Meta:
        model = ActivityLog
        fields = ['action', 'timestamp']

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        data['email'] = self.user.email
        
        if hasattr(self.user, 'profile') and self.user.profile.avatar:
            data['avatar'] = self.user.profile.avatar.url
        else:
            data['avatar'] = None
            
        return data