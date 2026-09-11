from typing import ClassVar

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

from misas.models import Servicio, Templo

MAX_IMAGEN_BYTES = 5 * 1024 * 1024


class TemploForm(forms.ModelForm):
    class Meta:
        model = Templo
        fields = ("nombre", "direccion", "alias", "imagen")
        labels: ClassVar[dict[str, str]] = {
            "nombre": "Nombre",
            "direccion": "Dirección",
            "alias": "Otro nombre conocido",
            "imagen": "Fotografía",
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
        }
        error_messages: ClassVar[dict[str, dict[str, str]]] = {
            "imagen": {
                "invalid": "El archivo no es una imagen válida.",
                "invalid_image": "El archivo no es una imagen válida.",
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
