# Create your views here.
from django.shortcuts import render_to_response


def default(request, nome = None):
    return render_to_response('default.html', 
                            { 'nome' : nome})
