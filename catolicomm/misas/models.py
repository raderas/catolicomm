from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract=True

class Templo(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=1000)
    alias = models.CharField("otro nombre conocido", max_length=100)

    def get_servicios(self) -> dict:
        servicios={}
        
        for servicio in self.servicio_set.all():
            dia_semana=servicio.get_dia_de_semana_display()
            tipo_servicio = servicio.get_tipo_servicio_display()
            if tipo_servicio not in servicios:
                servicios[tipo_servicio]={}
            hora_inicio = servicio.hora_inicio.strftime("%H:%M")
            if dia_semana in servicios[tipo_servicio]:
                servicios[tipo_servicio][dia_semana].append(hora_inicio)
            else:
                servicios[tipo_servicio][dia_semana] = [hora_inicio]

        return servicios
    
    def __str__(self):
        return f"Templo: {self.nombre}"

class Servicio(BaseModel):
    class DiasSemana(models.TextChoices):
        DOMINGO='DOM', _("Domingo")
        LUNES='LUN', _("Lunes")
        MARTES='MAR', _("Martes")
        MIERCOLES='MIE', _("Miércoles")
        JUEVES='JUE', _('Jueves')
        VIERNES='VIE', _("Viernes")
        SABADO='SAB', _("Sábado")

    class TipoServicio(models.TextChoices):
        MISA= 'MI', _('Eucaristia')
        CONFESIONES= 'CO', _('Confesiones')
        SANTISIMO= 'SA', _('Capilla del Santísimo')
        ADORACION='AD', _('Adoración Eucarística')

    id = models.UUIDField(primary_key=True, default = uuid.uuid4, editable=False)
    templo = models.ForeignKey(Templo, on_delete=models.CASCADE)
    tipo_servicio=models.CharField(max_length=2,choices=TipoServicio.choices)
    # el dia de la semana es un entero entre 1 y 7 siendo 1=Domingo
    dia_de_semana = models.CharField(max_length=3,choices=DiasSemana.choices)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField(blank=True,null=True)

    def get_nombre_dia(self) -> str:
        """Devuelve el nombre del dia de la semana como string legible"""
        return self.get_dia_de_semana_display()
    
    def __str__(self):
        return f"{self.get_tipo_servicio_display()} en {self.templo.nombre} {self.get_nombre_dia()} - {self.hora_inicio}"

