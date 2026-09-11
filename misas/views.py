from typing import Any

from django.contrib.auth.decorators import login_required
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic

from .forms import ServicioForm, TemploForm
from .models import Templo


class TemploView(generic.DetailView):
    model = Templo
    template_name = "misas/templo.html"


class IndexView(generic.ListView):
    template_name = "misas/index.html"
    context_object_name = "lista_templos"

    def get_queryset(self) -> QuerySet[Any, Any]:
        """Devolver listado de templos."""
        return Templo.objects.all()[:5]


def index(request):
    lista_templos = Templo.objects.all()
    context = {"lista_templos": lista_templos}
    return render(request, "misas/index.html", context)


def templo(request, templo_id):
    templo = get_object_or_404(Templo, pk=templo_id)
    return render(request, "misas/templo.html", {"templo": templo})


@login_required
def templo_form(request):
    if request.method == "POST":
        form = TemploForm(request.POST, request.FILES)
        if form.is_valid():
            templo = form.save()
            return redirect("misas:templo", pk=templo.pk)
    else:
        form = TemploForm()
    return render(request, "misas/newtemplo.html", {"form": form})


@login_required
def templo_edit(request, id_templo):
    templo = get_object_or_404(Templo, pk=id_templo)
    if request.method == "POST":
        form = TemploForm(request.POST, request.FILES, instance=templo)
        if form.is_valid():
            form.save()
            return redirect("misas:templo", pk=templo.pk)
    else:
        form = TemploForm(instance=templo)
    return render(request, "misas/edit_templo.html", {"form": form, "templo": templo})


@login_required
def templo_servicios_edit(request, id_templo):
    templo = get_object_or_404(Templo, pk=id_templo)
    ctx = {}

    if request.method == "POST":
        form = ServicioForm(request.POST, id_templo=id_templo)
        if form.is_valid():
            new_servicio = form.save(commit=False)
            new_servicio.templo = templo
            new_servicio.save()
            form = ServicioForm(id_templo=id_templo)
            ctx["mensaje"] = "Servicio guardado."
    else:
        form = ServicioForm(id_templo=id_templo)

    ctx["form"] = form
    ctx["templo"] = templo
    return render(request, "misas/edit_servicios.html", ctx)
