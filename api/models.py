from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# 1. CORE BOOK MODEL (Updated for IT Bookstore & Iframe Reader)
class Book(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="books")
    # We rename 'google_book_id' logic to handle ISBN13 from IT Bookstore
    google_book_id = models.CharField(max_length=255, blank=True, null=True) 
    title = models.CharField(max_length=255)
    authors = models.CharField(max_length=255, blank=True, null=True, default="Technical Author")
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    preview_link = models.URLField(max_length=1000, blank=True, null=True)
    category = models.CharField(max_length=100, default="Technology")
    
    # NEW FIELDS FOR INTERNAL READER
    web_reader_link = models.URLField(max_length=1000, blank=True, null=True)
    is_ebook = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'google_book_id')

    def __str__(self):
        return self.title

# 2. ACTIVITY TRACKER
class ActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")
    action = models.CharField(max_length=255) 
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username}: {self.action}"

# 3. READING PROGRESS
class ReadingProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    google_book_id = models.CharField(max_length=255) # Store ISBN13 here
    current_page = models.IntegerField(default=1)
    last_read = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'google_book_id')

# 4. PROFILE LOGIC
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# --- SIGNALS ---

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=Book)
def log_book_activity(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            user=instance.user,
            action=f"Added '{instance.title}' to their tech library"
        )