# Create your views here.
from django.shortcuts import render_to_response

def default_view(request):
    return render_to_response('default.html')


def default_view_nome(request, nome):
    return render_to_response('default.html', { 'nome' : nome })



