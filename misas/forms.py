from typing import ClassVar

from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    UserCreationForm,
)
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _

from misas.models import Servicio, Templo

UserModel = get_user_model()

MAX_IMAGEN_BYTES = 5 * 1024 * 1024


class TemploForm(forms.ModelForm):
    class Meta:
        model = Templo
        fields = ("nombre", "direccion", "alias", "imagen", "facebook")
        labels: ClassVar[dict[str, str]] = {
            "nombre": "Nombre",
            "direccion": "Dirección",
            "alias": "Otro nombre conocido",
            "imagen": "Fotografía",
            "facebook": "Facebook",
        }
        widgets: ClassVar[dict[str, forms.Widget]] = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "alias": forms.TextInput(attrs={"class": "form-control"}),
            "imagen": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp",
                }
            ),
            "facebook": forms.URLInput(attrs={"class": "form-control"}),
        }
        error_messages: ClassVar[dict[str, dict[str, str]]] = {
            "imagen": {
                "invalid": "El archivo no es una imagen válida.",
                "invalid_image": "El archivo no es una imagen válida.",
            },
            "facebook": {
                "invalid": "Introduce una dirección web válida.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["imagen"].required = False
        self.fields["imagen"].validators.append(
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp"],
                message="Sube una imagen JPEG, PNG o WebP.",
            )
        )
        self.fields["facebook"].required = False
        self.fields["facebook"].assume_scheme = "https"

    def clean_facebook(self):
        facebook = self.cleaned_data.get("facebook") or ""
        facebook = facebook.strip()
        if not facebook:
            return ""
        if not facebook.startswith(("http://", "https://")):
            facebook = f"https://{facebook}"
        return facebook

    def clean_imagen(self):
        imagen = self.cleaned_data.get("imagen")
        if not imagen:
            return imagen
        size = getattr(imagen, "size", None)
        if size is not None and size > MAX_IMAGEN_BYTES:
            raise ValidationError("La fotografía no puede superar 5 MB.")
        return imagen


class ServicioForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.id_templo = kwargs.pop("id_templo", None)
        super().__init__(*args, **kwargs)
        for name in ("tipo_servicio", "dia_de_semana"):
            choices = list(self.fields[name].choices)
            if choices and choices[0][0] == "":
                choices[0] = ("", "Seleccione una opción")
                self.fields[name].choices = choices

    class Meta:
        model = Servicio
        fields = ("tipo_servicio", "dia_de_semana", "hora_inicio", "hora_fin")
        labels: ClassVar[dict[str, str]] = {
            "tipo_servicio": "Tipo de servicio",
            "dia_de_semana": "Día de la semana",
            "hora_inicio": "Hora de inicio",
            "hora_fin": "Hora de fin",
        }
        widgets: ClassVar[dict[str, forms.Widget]] = {
            "tipo_servicio": forms.Select(attrs={"class": "form-select"}),
            "dia_de_semana": forms.Select(attrs={"class": "form-select"}),
            "hora_inicio": forms.TimeInput(
                format="%H:%M",
                attrs={"class": "form-control", "type": "time"},
            ),
            "hora_fin": forms.TimeInput(
                format="%H:%M",
                attrs={"class": "form-control", "type": "time"},
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get("hora_inicio")
        hora_fin = cleaned_data.get("hora_fin")
        tipo_servicio = cleaned_data.get("tipo_servicio")
        dia_de_semana = cleaned_data.get("dia_de_semana")

        if hora_inicio and hora_fin and hora_fin < hora_inicio:
            self.add_error(
                "hora_fin",
                "La hora de fin no puede ser anterior a la hora de inicio.",
            )
            return cleaned_data

        if not (self.id_templo and tipo_servicio and dia_de_semana and hora_inicio):
            return cleaned_data

        siblings = Servicio.objects.filter(
            templo_id=self.id_templo,
            tipo_servicio=tipo_servicio,
            dia_de_semana=dia_de_semana,
        )
        if self.instance.pk:
            siblings = siblings.exclude(pk=self.instance.pk)

        for existente in siblings:
            if existente.hora_inicio == hora_inicio:
                raise ValidationError(
                    "Ya existe un servicio del mismo tipo, el mismo día y a la misma hora de inicio."
                )
            if not existente.hora_fin:
                continue
            if hora_fin:
                overlaps = (
                    hora_inicio < existente.hora_fin
                    and existente.hora_inicio < hora_fin
                )
            else:
                overlaps = existente.hora_inicio <= hora_inicio < existente.hora_fin
            if overlaps:
                raise ValidationError(
                    "El horario se solapa con otro servicio del mismo tipo ese día."
                )

        return cleaned_data


class CrearCuentaForm(UserCreationForm):
    email = forms.EmailField(
        label="Correo de contacto",
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "autocomplete": "email"}
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = UserModel
        fields = ("username", "email")
        labels: ClassVar[dict[str, str]] = {
            "username": "Usuario",
        }
        widgets: ClassVar[dict[str, forms.Widget]] = {
            "username": forms.TextInput(
                attrs={"class": "form-control", "autocomplete": "username"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Contraseña"
        self.fields["password2"].label = "Confirmación de contraseña"
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "autocomplete": "new-password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "autocomplete": "new-password"}
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_active = False
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user


class AutenticacionForm(AuthenticationForm):
    error_messages: ClassVar[dict[str, str]] = {
        **AuthenticationForm.error_messages,
        "inactive": _(
            "Tu cuenta aún no está confirmada. Revisa tu correo o reenvía el "
            "enlace de confirmación."
        ),
    }

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if username is not None and password:
            try:
                user = UserModel._default_manager.get_by_natural_key(username)
            except UserModel.DoesNotExist:
                user = None
            if (
                user is not None
                and not user.is_active
                and user.check_password(password)
            ):
                raise ValidationError(
                    self.error_messages["inactive"],
                    code="inactive",
                )
            self.user_cache = authenticate(
                self.request, username=username, password=password
            )
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


class UsernamePasswordResetForm(PasswordResetForm):
    username = forms.CharField(
        label="Usuario",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "username",
                "autofocus": True,
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("email")

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data["email"] = ""
        return cleaned_data

    def get_users(self, email):
        username = self.cleaned_data.get("username")
        if not username:
            return
        try:
            user = UserModel._default_manager.get(username=username)
        except UserModel.DoesNotExist:
            return
        if user.is_active and user.email and user.has_usable_password():
            yield user


class ReenviarConfirmacionForm(forms.Form):
    username = forms.CharField(
        label="Usuario",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "username",
                "autofocus": True,
            }
        ),
    )
