from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, get_object_or_404

from .models import Templo, Misa

# Create your views here.
def index(request):
    lista_templos = Templo.objects.all()
    context= {"lista_templos": lista_templos}
    return render(request, 'misas/index.html', context)

def templo(request, templo_id):
    templo = get_object_or_404(Templo, pk=templo_id)
    return render(request, 'misas/templo.html', {'templo': templo})
