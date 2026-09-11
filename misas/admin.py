from django.contrib import admin

# Register your models here.
from .models import Servicio, Templo


class TemploAdmin(admin.ModelAdmin):
    list_display = ("nombre", "alias", "direccion")
    seach_fields = ("nombre", "alias")


class ServicioAdmin(admin.ModelAdmin):
    list_filter = ("tipo_servicio",)


admin.site.register(Templo, TemploAdmin)
admin.site.register(Servicio, ServicioAdmin)
