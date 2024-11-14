from django.http import HttpResponse, FileResponse, Http404
from django.shortcuts import render
import os
# Create your views here.

def project(request):
    context = {
        'file1': 'documents/Project Plan Fall 2024 Presentation.pdf',
        'file2': 'documents/Milestone One Progress Evaluation.pdf',
        'file3': 'documents/Milestone One Fall 2024 Senior Design.pdf'
    }
    return render(request, 'main/project.html', context)

def serve_file(request, file_path):
    file_full_path = os.path.join('media', file_path)
    if os.path.exists(file_full_path):
        return FileResponse(open(file_full_path, 'rb'))
    else:
        raise Http404("File not found")

def home(request):
    return render(request, 'main/home.html')


# def open_file(request, *args, **kwargs):
#     path = str(kwargs['p'])

#     file_path = 'your path'
#     if os.path.exists(file_path):
#         with open(file_path, 'rb') as fh:
#             response = HttpResponse(
#                 fh.read(), content_type="application/vnd.ms-excel")
#             response['Content-Disposition'] = 'inline; filename=' + \
#                 os.path.basename(file_path)
#             return response
#     raise Http404
