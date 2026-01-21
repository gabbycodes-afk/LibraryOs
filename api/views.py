import requests
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Profile, ReadingProgress, Book, ActivityLog 
from .serializers import (
    UserSerializer, 
    MyTokenObtainPairSerializer, 
    ProfileSerializer,
    BookSerializer,
    ActivityLogSerializer 
)
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.parsers import MultiPartParser, FormParser

# 1. AUTHENTICATION VIEWS
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

# 2. LIBRARY MANAGEMENT
class BookListCreate(generics.ListCreateAPIView):
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Book.objects.filter(user=self.request.user).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        isbn13 = request.data.get("google_book_id")
        if isbn13 and Book.objects.filter(user=self.request.user, google_book_id=isbn13).exists():
            return Response(
                {"detail": "This tech book is already in your library."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BookDetail(generics.RetrieveDestroyAPIView):
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Book.objects.filter(user=self.request.user)

# 3. IT BOOKSTORE SEARCH VIEW (Optimized with Google Embedded Reader)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_books(request):
    query = request.query_params.get('q', '')
    
    if not query:
        return Response([])

    url = f"https://api.itbook.store/1.0/search/{query}"
    
    try:
        response = requests.get(url)
        data = response.json()
    except Exception:
        return Response({"error": "IT Bookstore API service unreachable"}, status=400)
    
    formatted_results = []
    for item in data.get('books', []):
        isbn13 = item.get('isbn13')
        
        formatted_results.append({
            "google_book_id": isbn13,
            "title": item.get('title', 'Untitled'),
            "authors": item.get('subtitle') or "Technical Author", 
            "image_url": item.get('image'), 
            "description": item.get('subtitle', ''),
            "preview_link": item.get('url'), 
            "category": "Technology",
            "is_ebook": True,
            "is_readable": True,
            
            # THE FIX: Use Google Books Viewer to ensure a readable preview exists for your iframe
            # This uses the ISBN to find the book in Google's database and displays the embeddable viewer
            "web_reader_link": f"https://books.google.com/books?vid=ISBN{isbn13}&printsec=frontcover&output=embed",
            
            "is_search_result": True
        })
        
    return Response(formatted_results)

# 4. USER PROFILE & INTERACTION
class ProfileUpdateView(generics.UpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    def get_object(self):
        return self.request.user.profile

class ReadingProgressUpdate(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    def patch(self, request, *args, **kwargs):
        book_id = request.data.get("google_book_id")
        page = request.data.get("current_page")
        progress, created = ReadingProgress.objects.update_or_create(
            user=request.user, google_book_id=book_id,
            defaults={'current_page': page}
        )
        return Response({"status": "progress updated"})

class ActivityLogList(generics.ListAPIView):
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ActivityLog.objects.filter(user=self.request.user).order_by('-timestamp')[:10]