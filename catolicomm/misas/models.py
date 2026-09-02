from django.db import models
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

    def get_misas(self) -> dict:
        misas={}
        for misa in self.misa_set.all():
            if misa.dia_de_semana in misas:
                misas[misa.dia_de_semana].append(misa.hora_inicio.strftime("%H:%M"))
            else:
                misas[misa.dia_de_semana] = [misa.hora_inicio.strftime("%H:%M")]

        for i in range(1,8):
            if i in misas:
                misas[Misa.DIAS_SEMANA[i-1][1]]=misas.pop(i)

        return misas
    
    def __str__(self):
        return f"Templo: {self.nombre}"


class Misa(BaseModel):
    DIAS_SEMANA = [
        (1,'Domingo'),
        (2,'Lunes'),
        (3,'Martes'),
        (4,'Miercoles'),
        (5,'Jueves'),
        (6,'Viernes'),
        (7,'Sabado')
    ]

    id = models.UUIDField(primary_key=True, default = uuid.uuid4, editable=False)
    templo = models.ForeignKey(Templo, on_delete=models.CASCADE)
    # el dia de la semana es un entero entre 1 y 7 siendo 1=Domingo
    dia_de_semana = models.PositiveSmallIntegerField(choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()

    def get_nombre_dia(self) -> str:
        """Devuelve el nombre del dia de la semana como string legible"""
        return self.get_dia_de_semana_display()
    
    def __str__(self):
        return f"Misa en {self.templo.nombre} {self.get_nombre_dia()} - {self.hora_inicio}"


