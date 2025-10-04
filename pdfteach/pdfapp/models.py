from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PDFFile(models.Model):
    FILE_TYPES = (
        ('pdf', 'PDF File'),
        ('word', 'Word Document'),
        ('image', 'Image File'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='pdfs/')
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    storage_used = models.BigIntegerField(default=0)  # in bytes
    max_storage = models.BigIntegerField(default=104857600)  # 100MB default
    
    def __str__(self):
        return self.user.username

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.subject} - {self.email}"
