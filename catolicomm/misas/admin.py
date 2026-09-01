from django.contrib import admin

# Register your models here.
from .models import Misa, Templo

admin.site.register(Misa)
admin.site.register(Templo)
