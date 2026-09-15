import datetime
import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Dict para homologar los dias con el resultado del numero de dia devuelto por datetime
DIAS_MAP = {
    "LUN": 0,
    "MAR": 1,
    "MIE": 2,
    "JUE": 3,
    "VIE": 4,
    "SAB": 5,
    "DOM": 6,
}


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


def format_hora_12h(value: datetime.time) -> str:
    """Display-only Spanish 12-hour clock. Does not change stored TimeField values."""
    hour = value.hour
    minute = value.minute
    if hour == 0:
        hour_12 = 12
        suffix = "a. m."
    elif hour < 12:
        hour_12 = hour
        suffix = "a. m."
    elif hour == 12:
        hour_12 = 12
        suffix = "p. m."
    else:
        hour_12 = hour - 12
        suffix = "p. m."
    return f"{hour_12}:{minute:02d} {suffix}"


class Templo(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=1000)
    alias = models.CharField(
        "otro nombre conocido", max_length=100, blank=True, default=""
    )
    imagen = models.ImageField(
        "Fotografía", upload_to="templos/", null=True, blank=True
    )
    facebook = models.URLField(
        "Facebook",
        max_length=500,
        blank=True,
        default="",
    )
    verificado = models.BooleanField(default=False)

    def revocar_verificacion(self) -> None:
        if not self.verificado:
            return
        self.verificado = False
        self.save(update_fields=["verificado"])

    def get_servicios(self) -> dict:
        servicios = {}

        for servicio in self.servicio_set.all():
            dia_semana = servicio.get_dia_de_semana_display()
            tipo_servicio = servicio.get_tipo_servicio_display()
            if tipo_servicio not in servicios:
                servicios[tipo_servicio] = {}
            hora_inicio = format_hora_12h(servicio.hora_inicio)
            if dia_semana in servicios[tipo_servicio]:
                servicios[tipo_servicio][dia_semana].append(hora_inicio)
            else:
                servicios[tipo_servicio][dia_semana] = [hora_inicio]

        return servicios

    def get_proxima_misa(self):
        """
        Retorna la tupla (instancia_servicio, datetime_proxima_misa) para la misa más cercana.
        Si se pasa un `templo`, filtra solo las misas de ese templo.
        """
        ahora = timezone.localtime(timezone.now())
        fecha_actual = ahora.date()
        dia_semana_actual = fecha_actual.weekday()  # Lunes: 0, Domingo: 6

        # 1. Obtener todas las misas
        misas = self.servicio_set.all().filter(tipo_servicio=Servicio.TipoServicio.MISA)

        candidatas = []

        for misa in misas:
            target_weekday = DIAS_MAP.get(misa.dia_de_semana)
            if target_weekday is None:
                continue

            # Calcular cuántos días faltan para la misa
            dias_diferencia = (target_weekday - dia_semana_actual) % 7

            fecha_misa = fecha_actual + datetime.timedelta(days=dias_diferencia)
            datetime_misa = timezone.make_aware(
                datetime.datetime.combine(fecha_misa, misa.hora_inicio)
            )

            # Si el evento es hoy pero la hora ya pasó, corresponde a la próxima semana (+7 días)
            if datetime_misa <= ahora:
                datetime_misa += datetime.timedelta(days=7)

            candidatas.append((misa, datetime_misa))

        if not candidatas:
            return None

        # 2. Retornar la misa con la fecha/hora más cercana
        candidatas.sort(key=lambda x: x[1])
        return candidatas[0]  # Retorna (Servicio, datetime_de_la_misa)

    def __str__(self):
        return f"Templo: {self.nombre}"


class Servicio(BaseModel):
    class DiasSemana(models.TextChoices):
        DOMINGO = "DOM", _("Domingo")
        LUNES = "LUN", _("Lunes")
        MARTES = "MAR", _("Martes")
        MIERCOLES = "MIE", _("Miércoles")
        JUEVES = "JUE", _("Jueves")
        VIERNES = "VIE", _("Viernes")
        SABADO = "SAB", _("Sábado")

    class TipoServicio(models.TextChoices):
        MISA = "MI", _("Eucaristia")
        CONFESIONES = "CO", _("Confesiones")
        SANTISIMO = "SA", _("Capilla del Santísimo")
        ADORACION = "AD", _("Adoración Eucarística")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    templo = models.ForeignKey(Templo, on_delete=models.CASCADE)
    tipo_servicio = models.CharField(max_length=2, choices=TipoServicio.choices)
    # el dia de la semana es un entero entre 1 y 7 siendo 1=Domingo
    dia_de_semana = models.CharField(max_length=3, choices=DiasSemana.choices)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField(blank=True, null=True)

    @classmethod
    def obtener_proxima_misa(cls, templo=None):
        """
        Retorna la tupla (instancia_servicio, datetime_proxima_misa) para la misa más cercana.
        Si se pasa un `templo`, filtra solo las misas de ese templo.
        """
        ahora = timezone.localtime(timezone.now())
        fecha_actual = ahora.date()
        dia_semana_actual = fecha_actual.weekday()  # Lunes: 0, Domingo: 6

        # 1. Obtener todas las misas
        misas = cls.objects.filter(tipo_servicio=cls.TipoServicio.MISA)
        if templo:
            misas = misas.filter(templo=templo)

        candidatas = []

        for misa in misas:
            target_weekday = DIAS_MAP.get(misa.dia_de_semana)
            if target_weekday is None:
                continue

            # Calcular cuántos días faltan para la misa
            dias_diferencia = (target_weekday - dia_semana_actual) % 7

            fecha_misa = fecha_actual + datetime.timedelta(days=dias_diferencia)
            datetime_misa = timezone.make_aware(
                datetime.datetime.combine(fecha_misa, misa.hora_inicio)
            )

            # Si el evento es hoy pero la hora ya pasó, corresponde a la próxima semana (+7 días)
            if datetime_misa <= ahora:
                datetime_misa += datetime.timedelta(days=7)

            candidatas.append((misa, datetime_misa))

        if not candidatas:
            return None

        # 2. Retornar la misa con la fecha/hora más cercana
        candidatas.sort(key=lambda x: x[1])
        return candidatas[0]  # Retorna (Servicio, datetime_de_la_misa)

    def get_nombre_dia(self) -> str:
        """Devuelve el nombre del dia de la semana como string legible"""
        return self.get_dia_de_semana_display()

    def __str__(self):
        return f"{self.get_tipo_servicio_display()} en {self.templo.nombre} {self.get_nombre_dia()} - {self.hora_inicio}"
