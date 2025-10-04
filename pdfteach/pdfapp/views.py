from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import PDFFile, Contact
from .forms import PDFUploadForm, ContactForm
import os
from django.conf import settings
from pathlib import Path
import pythoncom
from win32com import client
from PIL import Image
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_bytes
import base64

def home(request):
    return render(request, 'pdfapp/home.html')

def about(request):
    return render(request, 'pdfapp/about.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pdfapp:home')
    else:
        form = ContactForm()
    return render(request, 'pdfapp/contact.html', {'form': form})

@login_required
def search_files(request):
    query = request.GET.get('q', '')
    files = PDFFile.objects.filter(
        user=request.user,
        title__icontains=query
    )
    return render(request, 'pdfapp/search.html', {'files': files, 'query': query})

@login_required
def edit_pdf(request):
    if request.method == 'POST':
        try:
            if 'file' in request.FILES:
                pdf_file = request.FILES['file']
                # Read PDF file
                pdf_reader = PdfReader(pdf_file)
                
                # Convert first page to image for preview
                images = convert_from_bytes(pdf_file.read())
                if images:
                    # Convert image to base64 for display
                    buffered = io.BytesIO()
                    images[0].save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    
                    return JsonResponse({
                        'status': 'success',
                        'preview': img_str,
                        'pages': len(pdf_reader.pages)
                    })
            
            elif 'edited_pdf' in request.POST:
                # Handle saving edited PDF
                # This is where you'll implement the PDF editing logic
                return JsonResponse({'status': 'success'})
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return render(request, 'pdfapp/edit_pdf.html')

@login_required
def word_to_pdf(request):
    if request.method == 'POST':
        try:
            # Get the uploaded files
            files = request.FILES.getlist('files[]')
            
            if not files:
                return JsonResponse({'error': 'No files uploaded'}, status=400)
            
            # Create media directory if it doesn't exist
            media_dir = Path(settings.MEDIA_ROOT) / 'temp'
            media_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize Word application
            pythoncom.CoInitialize()
            word = client.Dispatch('Word.Application')
            
            # Convert each Word document to PDF
            pdf_paths = []
            for file in files:
                # Save the uploaded file
                word_path = media_dir / file.name
                with open(word_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                
                # Convert to PDF
                pdf_path = word_path.with_suffix('.pdf')
                doc = word.Documents.Open(str(word_path))
                doc.SaveAs(str(pdf_path), FileFormat=17)  # 17 represents PDF format
                doc.Close()
                
                pdf_paths.append(pdf_path)
            
            # Close Word application
            word.Quit()
            pythoncom.CoUninitialize()
            
            # If there's only one PDF, return it directly
            if len(pdf_paths) == 1:
                with open(pdf_paths[0], 'rb') as pdf_file:
                    response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="{pdf_paths[0].name}"'
                    return response
            
            # If there are multiple PDFs, merge them (you'll need PyPDF2 for this)
            # ... add PDF merging logic here ...
            
            # Clean up temporary files
            for path in [*pdf_paths, *[Path(f.name) for f in files]]:
                try:
                    os.remove(path)
                except:
                    pass
            
            return response
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return render(request, 'pdfapp/word_to_pdf.html')

@login_required
def image_to_pdf(request):
    if request.method == 'POST':
        try:
            # Get the uploaded files
            files = request.FILES.getlist('images[]')
            
            if not files:
                return JsonResponse({'error': 'No files uploaded'}, status=400)
            
            # Create a PDF
            pdf_buffer = io.BytesIO()
            
            # Create the first image as PDF
            first_image = Image.open(files[0])
            if first_image.mode != 'RGB':
                first_image = first_image.convert('RGB')
            
            # Save all images as PDF pages
            images = []
            for file in files:
                img = Image.open(file)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                images.append(img)
            
            # Save the first image and append others
            first_image.save(pdf_buffer, format='PDF', save_all=True, append_images=images[1:])
            
            # Prepare response
            pdf_buffer.seek(0)
            response = HttpResponse(pdf_buffer, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="images.pdf"'
            
            return response
            
        except Exception as e:
            import traceback
            print(traceback.format_exc())  # This will print the full error in console
            return JsonResponse({'error': str(e)}, status=500)
    
    return render(request, 'pdfapp/image_to_pdf.html')

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = form.save(commit=False)
            pdf_file.user = request.user
            pdf_file.save()
            return redirect('pdfapp:file_detail', file_id=pdf_file.id)
    else:
        form = PDFUploadForm()
    return render(request, 'pdfapp/upload.html', {'form': form})

@login_required
def file_detail(request, file_id):
    file = get_object_or_404(PDFFile, id=file_id, user=request.user)
    return render(request, 'pdfapp/file_detail.html', {'file': file})

@login_required
@require_POST
def delete_file(request, file_id):
    file = get_object_or_404(PDFFile, id=file_id, user=request.user)
    file.file.delete()
    file.delete()
    return redirect('pdfapp:dashboard')

@login_required
def dashboard(request):
    files = PDFFile.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(files, 10)
    page = request.GET.get('page')
    files = paginator.get_page(page)
    return render(request, 'pdfapp/dashboard.html', {'files': files})

@login_required
def user_files(request):
    files = PDFFile.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'pdfapp/user_files.html', {'files': files})

# API Views
@login_required
@require_POST
def api_upload(request):
    if request.FILES.get('file'):
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf_file = form.save(commit=False)
            pdf_file.user = request.user
            pdf_file.save()
            return JsonResponse({
                'status': 'success',
                'file_id': pdf_file.id,
                'url': pdf_file.file.url
            })
    return JsonResponse({'status': 'error'}, status=400)

@login_required
@require_POST
def api_save_pdf(request):
    # Logic for saving edited PDF
    return JsonResponse({'status': 'success'})
