from django.contrib import admin
from .models import Book, ActivityLog, ReadingProgress, Profile

# Registering the main models
admin.site.register(Book)
admin.site.register(ActivityLog)
admin.site.register(ReadingProgress)
admin.site.register(Profile)