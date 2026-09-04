from typing import Any

from django.db.models.query import QuerySet
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views import generic
from django.shortcuts import render, get_object_or_404

from .models import Templo, Servicio

class TemploView(generic.DetailView):
    model = Templo
    template_name = "misas/templo.html"

class IndexView(generic.ListView):
    template_name="misas/index.html"
    context_object_name= "lista_templos"

    def get_queryset(self) -> QuerySet[Any, Any]:
        """ Devolver listado de templos. """
        return Templo.objects.all()[:5]

def index(request):
    lista_templos = Templo.objects.all()
    context= {"lista_templos": lista_templos}
    return render(request, 'misas/index.html', context)

def templo(request, templo_id):
    templo = get_object_or_404(Templo, pk=templo_id)
    return render(request, 'misas/templo.html', {'templo': templo})

#TODO: Fix and use this view
def nuevo_templo(request):
    nuevo_templo=Templo()
    nuevo_templo.nombre=request.POST["nombre_templo"]
    nuevo_templo.direccion=request.POST["direccion_templo"]
    nuevo_templo.alias=request.POST["alias_templo"]

    try:
        nuevo_templo.save()
    except Exception as e:
        render(
            request,
            "misas/newtemplo.html",
            {
                "error_message": f"Error al registrar el templo {e.message}"
            }
        )
