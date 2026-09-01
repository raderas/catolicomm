from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("templos/<uuid:templo_id>/", views.templo, name="templo"), 
]