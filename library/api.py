from rest_framework import viewsets, permissions
from .models import Book
from .serializers import BookSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role in ['welfare', 'admin']:
            return Book.objects.all()
        elif self.request.user.role == 'student':
            return Book.objects.none()  # Students can only view their records, not books directly
        return Book.objects.none()
