from rest_framework import serializers
from .models import Book, StudentBookRecord, SchoolRecord

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class StudentBookRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentBookRecord
        fields = '__all__'

class SchoolRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolRecord
        fields = '__all__'
