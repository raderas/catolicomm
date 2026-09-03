from django.contrib import admin

# Register your models here.
from .models import Templo, Servicio

admin.site.register(Templo)
admin.site.register(Servicio)
