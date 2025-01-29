from django.http import HttpResponse, FileResponse, Http404
from django.shortcuts import render
import os
# Create your views here.

def project(request):
    context = {
        'projectPlan2Pres': 'documents/Project Plan Spring 2025 Presentation.pdf',
        'projectPlanPres': 'documents/Project Plan Fall 2024 Presentation.pdf',
        'milestone1Eval': 'documents/Milestone One Progress Evaluation.pdf',
        'milestone1Pres': 'documents/Milestone One Fall 2024 Senior Design.pdf',
        'milestone2Eval': 'documents/Milestone Two Progress Evaluation.pdf',
        'milestone2Pres': 'documents/Milestone Two Fall 2024 Senior Design.pdf',
        'milestone3Eval': 'documents/Milestone Three Progress Evaluation.pdf',
        'milestone3Pres': 'documents/Milestone Three Fall 2024 Senior Design.pdf',
        'projectPlan': 'documents/Project Plan.pdf',
        'projectPlan2': 'documents/Project Plan Spring.pdf',
        'webTesting': 'documents/Web Testing Plan.pdf',
    }
    return render(request, 'main/project.html', context)

def serve_file(request, file_path):
    file_full_path = os.path.join('static', file_path)
    if os.path.exists(file_full_path):
        return FileResponse(open(file_full_path, 'rb'))
    else:
        raise Http404("File not found")

def home(request):
    return render(request, 'main/home.html')


def research(request):
    return render(request, 'main/research.html')


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
