from django import forms
from .models import PDFFile, Contact

class PDFUploadForm(forms.ModelForm):
    class Meta:
        model = PDFFile
        fields = ['title', 'file', 'file_type']

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'subject', 'message'] 