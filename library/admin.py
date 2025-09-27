from django.contrib import admin
from .models import Book, StudentBookRecord, SchoolRecord

admin.site.register(Book)
admin.site.register(StudentBookRecord)
admin.site.register(SchoolRecord)
