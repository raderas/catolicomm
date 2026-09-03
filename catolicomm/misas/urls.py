from django.urls import path

from . import views

app_name = "misas"
urlpatterns = [
    path("", views.index, name="index"),
    #path("{% url misas:templo uuid:templo_id %}", views.TemploView.as_view(), name="templo"), 
    path("templo/<uuid:pk>/", views.TemploView.as_view(), name="templo"), 
    path("templo/nuevo/", views.templo, name="nuevo_templo"),
]