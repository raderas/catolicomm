from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetView
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMultiAlternatives
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import generic
from django.views.decorators.http import require_POST

from .forms import (
    CrearCuentaForm,
    ReenviarConfirmacionForm,
    ServicioForm,
    TemploForm,
    UsernamePasswordResetForm,
)
from .models import Templo
from .tokens import email_confirmation_token_generator

UserModel = get_user_model()


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
            templo = form.save(commit=False)
            if templo.verificado:
                templo.verificado = False
            templo.save()
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
            templo.revocar_verificacion()
            form = ServicioForm(id_templo=id_templo)
            ctx["mensaje"] = "Servicio guardado."
    else:
        form = ServicioForm(id_templo=id_templo)

    ctx["form"] = form
    ctx["templo"] = templo
    return render(request, "misas/edit_servicios.html", ctx)


@require_POST
@login_required
def templo_verificar(request, id_templo):
    if not request.user.is_staff:
        raise PermissionDenied
    templo = get_object_or_404(Templo, pk=id_templo)
    templo.verificado = request.POST.get("verificado") == "1"
    templo.save(update_fields=["verificado"])
    next_url = request.POST.get("next", "")
    ficha = reverse("misas:templo", args=[templo.pk])
    servicios = reverse("misas:templo_servicios", args=[templo.pk])
    if next_url in {ficha, servicios}:
        return redirect(next_url)
    return redirect("misas:templo", pk=templo.pk)


@login_required
def mi_perfil(request):
    return render(request, "misas/perfil.html")


def _redirect_authenticated(request):
    if request.user.is_authenticated:
        return redirect(settings.LOGIN_REDIRECT_URL)
    return None


def send_confirmation_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_confirmation_token_generator.make_token(user)
    confirm_url = request.build_absolute_uri(
        reverse("confirmar_correo", kwargs={"uidb64": uid, "token": token})
    )
    context = {"user": user, "confirm_url": confirm_url}
    subject = "".join(
        render_to_string("registration/confirmacion_subject.txt", context).splitlines()
    )
    body = render_to_string("registration/confirmacion_email.txt", context)
    EmailMultiAlternatives(subject, body, to=[user.email]).send()


def crear_cuenta(request):
    redirected = _redirect_authenticated(request)
    if redirected:
        return redirected
    if request.method == "POST":
        form = CrearCuentaForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_confirmation_email(request, user)
            return redirect("cuenta_creada")
    else:
        form = CrearCuentaForm()
    return render(request, "registration/crear_cuenta.html", {"form": form})


def cuenta_creada(request):
    redirected = _redirect_authenticated(request)
    if redirected:
        return redirected
    return render(request, "registration/cuenta_creada.html")


def confirmar_correo(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel.objects.get(pk=uid)
    except (
        TypeError,
        ValueError,
        OverflowError,
        UserModel.DoesNotExist,
        UnicodeDecodeError,
    ):
        user = None

    if user is not None and user.is_active:
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return render(
            request,
            "registration/confirmacion_invalida.html",
            {"ya_confirmada": True},
        )

    if user is not None and email_confirmation_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=["is_active"])
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect(settings.LOGIN_REDIRECT_URL)

    return render(
        request,
        "registration/confirmacion_invalida.html",
        {"ya_confirmada": False},
    )


def reenviar_confirmacion(request):
    redirected = _redirect_authenticated(request)
    if redirected:
        return redirected
    if request.method == "POST":
        form = ReenviarConfirmacionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            user = UserModel.objects.filter(username=username).first()
            if user is not None and not user.is_active and user.email:
                send_confirmation_email(request, user)
            return render(
                request,
                "registration/reenviar_confirmacion.html",
                {"form": form, "enviado": True},
            )
    else:
        form = ReenviarConfirmacionForm()
    return render(
        request,
        "registration/reenviar_confirmacion.html",
        {"form": form, "enviado": False},
    )


class VisitantePasswordResetView(PasswordResetView):
    form_class = UsernamePasswordResetForm
    template_name = "registration/password_reset_form.html"
    email_template_name = "registration/password_reset_email.html"
    subject_template_name = "registration/password_reset_subject.txt"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)


class VisitantePasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "registration/password_reset_confirm.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        return super().dispatch(request, *args, **kwargs)
