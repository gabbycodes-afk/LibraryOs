from django.urls import path
from .views import (
    MyTokenObtainPairView,
    CreateUserView,
    BookListCreate, 
    BookDetail,            # Added
    ProfileUpdateView,
    ReadingProgressUpdate,
    search_books,
    ActivityLogList        # Added for Dashboard
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('user/register/', CreateUserView.as_view(), name='register'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Library Routes
    path('books/', BookListCreate.as_view(), name='book-list'),
    path('books/<int:pk>/', BookDetail.as_view(), name='book-detail'), # CRITICAL for Reader.jsx
    path('books/search/', search_books, name='search_books'),
    
    # Profile & Activity
    path('profile/avatar/', ProfileUpdateView.as_view(), name='profile-avatar'),
    path('progress/', ReadingProgressUpdate.as_view(), name='progress-update'),
    path('activity/', ActivityLogList.as_view(), name='activity-list'), # For Dashboard
]