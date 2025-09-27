from rest_framework import viewsets, permissions
from .models import Book, StudentBookRecord, SchoolRecord
from .serializers import BookSerializer, StudentBookRecordSerializer, SchoolRecordSerializer

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role in ['librarian', 'admin']:
            return Book.objects.all()
        elif self.request.user.role == 'student':
            return Book.objects.none()  # Students can only view their records, not books directly
        return Book.objects.none()

class StudentBookRecordViewSet(viewsets.ModelViewSet):
    queryset = StudentBookRecord.objects.all()
    serializer_class = StudentBookRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'student':
            return StudentBookRecord.objects.filter(student=self.request.user)
        elif self.request.user.role in ['librarian', 'admin']:
            return StudentBookRecord.objects.all()
        return StudentBookRecord.objects.none()

class SchoolRecordViewSet(viewsets.ModelViewSet):
    queryset = SchoolRecord.objects.all()
    serializer_class = SchoolRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'student':
            return SchoolRecord.objects.filter(student=self.request.user)
        elif self.request.user.role in ['librarian', 'admin']:
            return SchoolRecord.objects.all()
        return SchoolRecord.objects.none()
