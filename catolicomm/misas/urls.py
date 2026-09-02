from django.urls import path

from . import views

app_name = "misas"
urlpatterns = [
    path("", views.index, name="index"),
    path("templo/<uuid:templo_id>/", views.templo, name="templo"), 
    path("templo/nuevo/", views.templo, name="nuevo_templo"),
]