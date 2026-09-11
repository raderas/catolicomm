from django.urls import path

from . import views

app_name = "misas"
urlpatterns = [
    path("", views.index, name="index"),
    # path("{% url misas:templo uuid:templo_id %}", views.TemploView.as_view(), name="templo"),
    path("templos/", views.IndexView.as_view(), name="lista_templos"),
    path("templo/<uuid:pk>/", views.TemploView.as_view(), name="templo"),
    path("templo/nuevo/", views.templo_form, name="nuevo_templo"),
    path(
        "templo/<uuid:id_templo>/editar/",
        views.templo_edit,
        name="editar_templo",
    ),
    path(
        "templo/<uuid:id_templo>/servicios/",
        views.templo_servicios_edit,
        name="templo_servicios",
    ),
]
