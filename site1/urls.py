"""
URL configuration for site1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import include, path

from misas.forms import AutenticacionForm
from misas.views import (
    VisitantePasswordResetConfirmView,
    VisitantePasswordResetView,
    confirmar_correo,
    crear_cuenta,
    cuenta_creada,
    reenviar_confirmacion,
)

urlpatterns = [
    path("misas/", include("misas.urls")),
    path(
        "accounts/login/",
        LoginView.as_view(
            redirect_authenticated_user=True,
            authentication_form=AutenticacionForm,
        ),
        name="login",
    ),
    path("accounts/crear-cuenta/", crear_cuenta, name="crear_cuenta"),
    path("accounts/cuenta-creada/", cuenta_creada, name="cuenta_creada"),
    path(
        "accounts/confirmar/<uidb64>/<token>/",
        confirmar_correo,
        name="confirmar_correo",
    ),
    path(
        "accounts/reenviar-confirmacion/",
        reenviar_confirmacion,
        name="reenviar_confirmacion",
    ),
    path(
        "accounts/password_reset/",
        VisitantePasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "accounts/reset/<uidb64>/<token>/",
        VisitantePasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    