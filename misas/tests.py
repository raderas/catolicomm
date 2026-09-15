import re
import uuid
from datetime import time
from io import BytesIO
from urllib.parse import urlparse

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image

from misas.forms import MAX_IMAGEN_BYTES
from misas.models import Servicio, Templo


class ServiciosEditorTestCase(TestCase):
    """Shared helpers: any authenticated user may open any temple (FR-010)."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="editor",
            password="password123",
        )
        self.templo = Templo.objects.create(
            nombre="Parroquia San José",
            direccion="Calle Principal 1",
        )
        self.client = Client()
        self.client.force_login(self.user)
        self.editor_url = reverse("misas:templo_servicios", args=[self.templo.id])

    def servicio_post_data(self, **overrides):
        data = {
            "tipo_servicio": Servicio.TipoServicio.MISA,
            "dia_de_semana": Servicio.DiasSemana.DOMINGO,
            "hora_inicio": "10:00",
        }
        data.update(overrides)
        return data

    def create_servicio(self, templo=None, **kwargs):
        defaults = {
            "templo": templo or self.templo,
            "tipo_servicio": Servicio.TipoServicio.MISA,
            "dia_de_semana": Servicio.DiasSemana.DOMINGO,
            "hora_inicio": time(10, 0),
        }
        defaults.update(kwargs)
        return Servicio.objects.create(**defaults)


class CrearServicioTests(ServiciosEditorTestCase):
    """US1: authenticated create form GET/POST and hora_fin validation."""

    def test_get_editor_authenticated_returns_200_with_create_fields(self):
        response = self.client.get(self.editor_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="tipo_servicio"')
        self.assertContains(response, 'name="dia_de_semana"')
        self.assertContains(response, 'name="hora_inicio"')
        self.assertContains(response, 'name="hora_fin"')
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertContains(response, "Guardar")

    def test_post_valid_service_persists_for_url_templo_not_body(self):
        other = Templo.objects.create(
            nombre="Otra Parroquia",
            direccion="Otra calle",
        )
        response = self.client.post(
            self.editor_url,
            self.servicio_post_data(
                hora_inicio="10:00",
                hora_fin="11:00",
                templo=str(other.id),
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Servicio.objects.count(), 1)
        servicio = Servicio.objects.get()
        self.assertEqual(servicio.templo_id, self.templo.id)
        self.assertEqual(servicio.tipo_servicio, Servicio.TipoServicio.MISA)
        self.assertEqual(servicio.dia_de_semana, Servicio.DiasSemana.DOMINGO)
        self.assertEqual(servicio.hora_inicio, time(10, 0))
        self.assertEqual(servicio.hora_fin, time(11, 0))

    def test_post_without_hora_fin_persists(self):
        response = self.client.post(self.editor_url, self.servicio_post_data())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Servicio.objects.count(), 1)
        self.assertIsNone(Servicio.objects.get().hora_fin)

    def test_post_hora_fin_before_hora_inicio_does_not_persist(self):
        response = self.client.post(
            self.editor_url,
            self.servicio_post_data(hora_inicio="11:00", hora_fin="10:00"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Servicio.objects.count(), 0)
        self.assertTrue(response.context["form"].errors)

    def test_unknown_templo_uuid_returns_404(self):
        url = reverse("misas:templo_servicios", args=[uuid.uuid4()])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class ListadoServiciosTests(ServiciosEditorTestCase):
    """US2: lower list from get_servicios(), or Spanish empty copy."""

    def test_get_shows_existing_servicios_grouped_without_fabricating(self):
        self.create_servicio(
            tipo_servicio=Servicio.TipoServicio.MISA,
            dia_de_semana=Servicio.DiasSemana.DOMINGO,
            hora_inicio=time(10, 0),
        )
        self.create_servicio(
            tipo_servicio=Servicio.TipoServicio.CONFESIONES,
            dia_de_semana=Servicio.DiasSemana.LUNES,
            hora_inicio=time(18, 0),
        )
        response = self.client.get(self.editor_url)
        self.assertEqual(response.status_code, 200)
        expected = self.templo.get_servicios()
        self.assertEqual(set(expected.keys()), {"Eucaristia", "Confesiones"})
        self.assertContains(response, "Eucaristia")
        self.assertContains(response, "Confesiones")
        self.assertContains(response, "Domingo")
        self.assertContains(response, "Lunes")
        self.assertContains(response, "10:00 a. m.")
        self.assertContains(response, "6:00 p. m.")
        list_html = response.content.decode().split("Servicios registrados", 1)[-1]
        self.assertIn("Eucaristia", list_html)
        self.assertIn("Confesiones", list_html)
        self.assertNotIn("Capilla del Santísimo", list_html)
        self.assertNotIn("Adoración Eucarística", list_html)

    def test_empty_templo_shows_spanish_empty_copy(self):
        response = self.client.get(self.editor_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.templo.get_servicios(), {})
        self.assertContains(
            response, "Aún no hay horarios registrados para este templo."
        )


class AccesoEditorTests(ServiciosEditorTestCase):
    """US3: anonymous visitors never see or POST the editor."""

    def test_anonymous_get_redirects_to_login_without_editor_body(self):
        anon = Client()
        response = anon.get(self.editor_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
        self.assertIn("next=", response.url)
        self.assertIn(self.editor_url, response.url)
        body = response.content.decode()
        self.assertNotIn('name="tipo_servicio"', body)
        self.assertNotIn("Servicios registrados", body)
        self.assertNotIn("Agregar servicio", body)

    def test_anonymous_post_redirects_and_does_not_insert(self):
        anon = Client()
        response = anon.post(self.editor_url, self.servicio_post_data())
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
        self.assertEqual(Servicio.objects.count(), 0)

    def test_login_then_next_returns_editor(self):
        anon = Client()
        login_url = reverse("login")
        response = anon.post(
            login_url,
            {
                "username": "editor",
                "password": "password123",
                "next": self.editor_url,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.editor_url)
        follow = anon.get(self.editor_url)
        self.assertEqual(follow.status_code, 200)
        self.assertContains(follow, "Agregar servicio")

    def test_public_index_and_templo_remain_accessible(self):
        anon = Client()
        index_response = anon.get(reverse("misas:index"))
        self.assertEqual(index_response.status_code, 200)
        templo_response = anon.get(reverse("misas:templo", args=[self.templo.id]))
        self.assertEqual(templo_response.status_code, 200)
        self.assertContains(templo_response, "Agregar Servicio")

    def test_login_page_is_spanish_and_themed(self):
        anon = Client()
        response = anon.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Iniciar sesión")
        self.assertContains(
            response, "card bg-surface border-subtle shadow-sm rounded-3"
        )
        self.assertContains(response, "form-control")
        self.assertContains(response, "btn btn-gold")


class ConflictosHorarioTests(ServiciosEditorTestCase):
    """US4: reject duplicates and interior overlaps of the same type."""

    def test_duplicate_same_type_day_start_does_not_persist(self):
        self.create_servicio(hora_inicio=time(10, 0))
        response = self.client.post(
            self.editor_url, self.servicio_post_data(hora_inicio="10:00")
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Servicio.objects.count(), 1)
        self.assertTrue(response.context["form"].errors)
        self.assertContains(response, "Ya existe un servicio del mismo tipo")

    def test_interior_overlap_with_hora_fin_does_not_persist(self):
        self.create_servicio(hora_inicio=time(10, 0), hora_fin=time(11, 0))
        response = self.client.post(
            self.editor_url,
            self.servicio_post_data(hora_inicio="10:30", hora_fin="10:45"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Servicio.objects.count(), 1)
        self.assertTrue(response.context["form"].errors)
        self.assertContains(response, "se solapa")

    def test_point_candidate_inside_existing_interval_does_not_persist(self):
        self.create_servicio(hora_inicio=time(10, 0), hora_fin=time(11, 0))
        response = self.client.post(
            self.editor_url,
            self.servicio_post_data(hora_inicio="10:30"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Servicio.objects.count(), 1)
        self.assertTrue(response.context["form"].errors)

    def test_adjacent_half_open_intervals_both_persist(self):
        self.create_servicio(hora_inicio=time(10, 0), hora_fin=time(11, 0))
        response = self.client.post(
            self.editor_url,
            self.servicio_post_data(hora_inicio="11:00", hora_fin="12:00"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Servicio.objects.count(), 2)
        self.assertFalse(response.context["form"].errors)

    def test_different_tipo_same_slot_persists(self):
        self.create_servicio(
            tipo_servicio=Servicio.TipoServicio.MISA,
            hora_inicio=time(10, 0),
        )
        response = self.client.post(
            self.editor_url,
            self.servicio_post_data(
                tipo_servicio=Servicio.TipoServicio.CONFESIONES,
                hora_inicio="10:00",
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Servicio.objects.count(), 2)

    def test_different_weekday_same_type_and_time_persists(self):
        self.create_servicio(
            dia_de_semana=Servicio.DiasSemana.DOMINGO,
            hora_inicio=time(10, 0),
        )
        response = self.client.post(
            self.editor_url,
            self.servicio_post_data(
                dia_de_semana=Servicio.DiasSemana.LUNES,
                hora_inicio="10:00",
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Servicio.objects.count(), 2)

    def test_existing_without_hora_fin_only_duplicate_start_is_rejected(self):
        self.create_servicio(hora_inicio=time(10, 0), hora_fin=None)
        overlap_candidate = self.client.post(
            self.editor_url,
            self.servicio_post_data(hora_inicio="10:30", hora_fin="11:00"),
        )
        self.assertEqual(overlap_candidate.status_code, 200)
        self.assertEqual(Servicio.objects.count(), 2)
        duplicate = self.client.post(
            self.editor_url,
            self.servicio_post_data(hora_inicio="10:00"),
        )
        self.assertEqual(duplicate.status_code, 200)
        self.assertEqual(Servicio.objects.count(), 2)
        self.assertTrue(duplicate.context["form"].errors)

    def test_rejected_post_leaves_lower_list_unchanged(self):
        self.create_servicio(hora_inicio=time(10, 0), hora_fin=time(11, 0))
        before = self.templo.get_servicios()
        response = self.client.post(
            self.editor_url,
            self.servicio_post_data(hora_inicio="10:00"),
        )
        self.templo.refresh_from_db()
        self.assertEqual(self.templo.get_servicios(), before)
        list_html = response.content.decode().split("Servicios registrados", 1)[-1]
        self.assertIn("10:00 a. m.", list_html)
        self.assertEqual(list_html.count("10:00 a. m."), 1)


def make_png_file(name="foto.png", size=(8, 8), color=(200, 40, 40)):
    buf = BytesIO()
    Image.new("RGB", size, color).save(buf, format="PNG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")


class TemploFichaTestCase(TestCase):
    """Shared helpers for temple create/edit. Any authenticated user may edit any temple (FR-014)."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="editor",
            password="password123",
        )
        self.templo = Templo.objects.create(
            nombre="Parroquia San José",
            direccion="Calle Principal 1",
            alias="San José",
        )
        self.client = Client()
        self.client.force_login(self.user)
        self.nuevo_url = reverse("misas:nuevo_templo")
        self.ficha_url = reverse("misas:templo", args=[self.templo.id])

    @property
    def edit_url(self):
        return reverse("misas:editar_templo", args=[self.templo.id])

    def templo_post_data(self, **overrides):
        data = {
            "nombre": "Parroquia Nueva",
            "direccion": "Avenida Central 10",
            "alias": "",
        }
        data.update(overrides)
        return data


class CrearTemploTests(TemploFichaTestCase):
    """US1: authenticated create with optional photo."""

    def test_get_create_authenticated_returns_200_with_fields(self):
        response = self.client.get(self.nuevo_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="nombre"')
        self.assertContains(response, 'name="direccion"')
        self.assertContains(response, 'name="alias"')
        self.assertContains(response, 'name="imagen"')
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertContains(response, "Guardar")

    def test_post_without_photo_inserts_and_ficha_shows_placeholder(self):
        before = Templo.objects.count()
        response = self.client.post(self.nuevo_url, self.templo_post_data())
        self.assertEqual(Templo.objects.count(), before + 1)
        created = Templo.objects.get(nombre="Parroquia Nueva")
        self.assertFalse(created.imagen)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("misas:templo", args=[created.id]))
        ficha = self.client.get(response.url)
        self.assertEqual(ficha.status_code, 200)
        self.assertContains(ficha, "bi-church")
        self.assertNotContains(ficha, 'src=""')

    def test_post_with_valid_png_persists_and_public_pages_show_url(self):
        response = self.client.post(
            self.nuevo_url,
            self.templo_post_data(imagen=make_png_file()),
        )
        created = Templo.objects.get(nombre="Parroquia Nueva")
        self.assertTrue(created.imagen)
        self.assertEqual(response.status_code, 302)
        ficha = self.client.get(response.url)
        self.assertContains(ficha, created.imagen.url)
        listing = self.client.get(reverse("misas:index"))
        self.assertContains(listing, created.imagen.url)

    def test_post_missing_nombre_or_direccion_does_not_insert(self):
        before = Templo.objects.count()
        missing_nombre = self.client.post(
            self.nuevo_url,
            self.templo_post_data(nombre=""),
        )
        self.assertEqual(missing_nombre.status_code, 200)
        self.assertTrue(missing_nombre.context["form"].errors)
        missing_direccion = self.client.post(
            self.nuevo_url,
            self.templo_post_data(direccion=""),
        )
        self.assertEqual(missing_direccion.status_code, 200)
        self.assertEqual(Templo.objects.count(), before)

    def test_post_non_image_or_oversized_does_not_insert(self):
        before = Templo.objects.count()
        txt = SimpleUploadedFile("nota.txt", b"no es imagen", content_type="text/plain")
        response = self.client.post(self.nuevo_url, self.templo_post_data(imagen=txt))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        huge = SimpleUploadedFile(
            "foto.png",
            b"x" * (MAX_IMAGEN_BYTES + 1),
            content_type="image/png",
        )
        huge_response = self.client.post(
            self.nuevo_url, self.templo_post_data(imagen=huge)
        )
        self.assertEqual(huge_response.status_code, 200)
        self.assertEqual(Templo.objects.count(), before)


class EditarTemploTextoTests(TemploFichaTestCase):
    """US2: edit nombre, direccion, alias independently."""

    def test_get_edit_authenticated_returns_200_with_current_values(self):
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="nombre"')
        self.assertContains(response, self.templo.nombre)
        self.assertContains(response, self.templo.direccion)
        self.assertContains(response, self.templo.alias)
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertContains(response, "Guardar")

    def test_post_changing_only_nombre_leaves_other_text_unchanged(self):
        response = self.client.post(
            self.edit_url,
            {
                "nombre": "Parroquia San José Actualizada",
                "direccion": self.templo.direccion,
                "alias": self.templo.alias,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.ficha_url)
        self.templo.refresh_from_db()
        self.assertEqual(self.templo.nombre, "Parroquia San José Actualizada")
        self.assertEqual(self.templo.direccion, "Calle Principal 1")
        self.assertEqual(self.templo.alias, "San José")

    def test_post_empty_nombre_or_direccion_does_not_overwrite(self):
        response = self.client.post(
            self.edit_url,
            {
                "nombre": "",
                "direccion": self.templo.direccion,
                "alias": self.templo.alias,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.templo.refresh_from_db()
        self.assertEqual(self.templo.nombre, "Parroquia San José")
        empty_direccion = self.client.post(
            self.edit_url,
            {
                "nombre": self.templo.nombre,
                "direccion": "",
                "alias": self.templo.alias,
            },
        )
        self.assertEqual(empty_direccion.status_code, 200)
        self.templo.refresh_from_db()
        self.assertEqual(self.templo.direccion, "Calle Principal 1")

    def test_unknown_templo_uuid_returns_404(self):
        url = reverse("misas:editar_templo", args=[uuid.uuid4()])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class EditarTemploFotoTests(TemploFichaTestCase):
    """US3: add, replace, or keep photo on edit."""

    def test_add_photo_to_templo_without_imagen(self):
        self.assertFalse(self.templo.imagen)
        response = self.client.post(
            self.edit_url,
            {
                "nombre": self.templo.nombre,
                "direccion": self.templo.direccion,
                "alias": self.templo.alias,
                "imagen": make_png_file(),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.templo.refresh_from_db()
        self.assertTrue(self.templo.imagen)
        ficha = self.client.get(self.ficha_url)
        self.assertContains(ficha, self.templo.imagen.url)

    def test_replace_existing_photo(self):
        self.templo.imagen = make_png_file("antes.png", color=(10, 10, 10))
        self.templo.save()
        old_name = self.templo.imagen.name
        response = self.client.post(
            self.edit_url,
            {
                "nombre": self.templo.nombre,
                "direccion": self.templo.direccion,
                "alias": self.templo.alias,
                "imagen": make_png_file("despues.png", color=(20, 80, 20)),
            },
        )
        self.assertEqual(response.status_code, 302)
        self.templo.refresh_from_db()
        self.assertTrue(self.templo.imagen)
        self.assertNotEqual(self.templo.imagen.name, old_name)
        ficha = self.client.get(self.ficha_url)
        self.assertContains(ficha, self.templo.imagen.url)

    def test_post_without_new_file_keeps_imagen(self):
        self.templo.imagen = make_png_file("queda.png")
        self.templo.save()
        kept = self.templo.imagen.name
        response = self.client.post(
            self.edit_url,
            {
                "nombre": self.templo.nombre,
                "direccion": self.templo.direccion,
                "alias": "Otro alias",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.templo.refresh_from_db()
        self.assertEqual(self.templo.imagen.name, kept)
        self.assertEqual(self.templo.alias, "Otro alias")

    def test_invalid_or_oversized_file_does_not_change_existing(self):
        self.templo.imagen = make_png_file("original.png")
        self.templo.save()
        kept = self.templo.imagen.name
        txt = SimpleUploadedFile("nota.txt", b"no es imagen", content_type="text/plain")
        response = self.client.post(
            self.edit_url,
            {
                "nombre": "Nombre hackeado",
                "direccion": self.templo.direccion,
                "alias": self.templo.alias,
                "imagen": txt,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.templo.refresh_from_db()
        self.assertEqual(self.templo.nombre, "Parroquia San José")
        self.assertEqual(self.templo.imagen.name, kept)
        huge = SimpleUploadedFile(
            "foto.png",
            b"x" * (MAX_IMAGEN_BYTES + 1),
            content_type="image/png",
        )
        huge_response = self.client.post(
            self.edit_url,
            {
                "nombre": "Nombre hackeado",
                "direccion": self.templo.direccion,
                "alias": self.templo.alias,
                "imagen": huge,
            },
        )
        self.assertEqual(huge_response.status_code, 200)
        self.templo.refresh_from_db()
        self.assertEqual(self.templo.nombre, "Parroquia San José")
        self.assertEqual(self.templo.imagen.name, kept)


class AccesoFichaTemploTests(TemploFichaTestCase):
    """US4: anonymous visitors never see or POST create/edit."""

    def test_anonymous_get_create_and_edit_redirect_to_login(self):
        anon = Client()
        create_response = anon.get(self.nuevo_url)
        self.assertEqual(create_response.status_code, 302)
        self.assertIn("/accounts/login/", create_response.url)
        self.assertIn("next=", create_response.url)
        self.assertIn(self.nuevo_url, create_response.url)
        self.assertNotIn('name="nombre"', create_response.content.decode())
        edit_response = anon.get(self.edit_url)
        self.assertEqual(edit_response.status_code, 302)
        self.assertIn("/accounts/login/", edit_response.url)
        self.assertIn(self.edit_url, edit_response.url)
        self.assertNotIn('name="nombre"', edit_response.content.decode())

    def test_anonymous_post_does_not_insert_or_update(self):
        anon = Client()
        before = Templo.objects.count()
        create_post = anon.post(self.nuevo_url, self.templo_post_data())
        self.assertEqual(create_post.status_code, 302)
        self.assertIn("/accounts/login/", create_post.url)
        self.assertEqual(Templo.objects.count(), before)
        edit_post = anon.post(
            self.edit_url,
            {
                "nombre": "No debe guardarse",
                "direccion": self.templo.direccion,
                "alias": self.templo.alias,
            },
        )
        self.assertEqual(edit_post.status_code, 302)
        self.templo.refresh_from_db()
        self.assertEqual(self.templo.nombre, "Parroquia San José")

    def test_login_then_next_returns_requested_screen(self):
        anon = Client()
        login_url = reverse("login")
        response = anon.post(
            login_url,
            {
                "username": "editor",
                "password": "password123",
                "next": self.edit_url,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.edit_url)
        follow = anon.get(self.edit_url)
        self.assertEqual(follow.status_code, 200)
        self.assertContains(follow, 'name="nombre"')

    def test_public_index_and_templo_remain_accessible_with_placeholder(self):
        anon = Client()
        index_response = anon.get(reverse("misas:index"))
        self.assertEqual(index_response.status_code, 200)
        self.assertContains(index_response, "bi-church")
        templo_response = anon.get(self.ficha_url)
        self.assertEqual(templo_response.status_code, 200)
        self.assertContains(templo_response, self.templo.nombre)
        self.assertContains(templo_response, "Editar templo")
        self.assertContains(templo_response, "Agregar Servicio")


class NavbarPerfilTestCase(TestCase):
    """Shared helpers for session-aware navbar and Mi perfil."""

    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="perfilista",
            password="password123",
            first_name="Ana",
            last_name="García",
            email="ana@example.com",
        )
        self.user_empty = user_model.objects.create_user(
            username="vacio",
            password="password123",
        )
        self.client = Client()
        self.anon = Client()
        self.templo = Templo.objects.create(
            nombre="Parroquia San José",
            direccion="Calle Principal 1",
        )

    @property
    def perfil_url(self):
        return reverse("misas:perfil")

    @property
    def index_url(self):
        return reverse("misas:index")

    @property
    def templo_url(self):
        return reverse("misas:templo", args=[self.templo.id])

    def login(self, user=None):
        self.client.force_login(user or self.user)


class NavbarIniciarSesionTests(NavbarPerfilTestCase):
    """US1: anonymous navbar shows Iniciar sesión; authenticated navbar hides it."""

    def test_anonymous_index_and_templo_show_spanish_login_link(self):
        for url in (self.index_url, self.templo_url):
            with self.subTest(url=url):
                response = self.anon.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, ">Iniciar sesión</a>")
                self.assertContains(response, reverse("login"))
                self.assertNotContains(response, ">Login</a>")
                self.assertNotContains(response, "Mi perfil")

    def test_authenticated_index_hides_iniciar_sesion(self):
        self.login()
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, ">Iniciar sesión</a>")


class NavbarMiPerfilTests(NavbarPerfilTestCase):
    """US2: authenticated navbar shows Mi perfil with icon; anonymous does not."""

    def test_authenticated_index_shows_mi_perfil_with_icon(self):
        self.login()
        response = self.client.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mi perfil")
        self.assertContains(response, "bi-person-circle")
        self.assertContains(response, self.perfil_url)
        self.assertNotContains(response, ">Iniciar sesión</a>")

    def test_anonymous_index_hides_mi_perfil(self):
        response = self.anon.get(self.index_url)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Mi perfil")


class MiPerfilConsultaTests(NavbarPerfilTestCase):
    """US3: authenticated user sees own account fields; empties show No registrado."""

    def test_filled_profile_shows_own_fields(self):
        self.login()
        response = self.client.get(self.perfil_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Usuario")
        self.assertContains(response, "Nombre")
        self.assertContains(response, "Apellidos")
        self.assertContains(response, "Correo electrónico")
        self.assertContains(response, "Fecha de alta")
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.user.first_name)
        self.assertContains(response, self.user.last_name)
        self.assertContains(response, self.user.email)
        self.assertContains(response, str(self.user.date_joined.year))
        self.assertContains(
            response, "card bg-surface border-subtle shadow-sm rounded-3"
        )
        self.assertNotContains(response, self.user.password)
        self.assertNotContains(response, "password123")
        self.assertNotContains(response, 'name="first_name"')
        self.assertNotContains(response, "Guardar")
        self.assertContains(response, "Cerrar sesión")
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertContains(response, "fw-medium active")

    def test_empty_optional_fields_show_no_registrado(self):
        self.login(self.user_empty)
        response = self.client.get(self.perfil_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user_empty.username)
        self.assertContains(response, "No registrado")
        self.assertNotContains(response, self.user.username)
        self.assertNotContains(response, self.user.email)

    def test_second_user_does_not_see_first_username(self):
        other = get_user_model().objects.create_user(
            username="otro",
            password="password123",
        )
        self.login(other)
        response = self.client.get(self.perfil_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "otro")
        self.assertNotContains(response, self.user.username)


class MiPerfilAuthTests(NavbarPerfilTestCase):
    """US4: login wall, next return, logout POST, authenticated login redirect."""

    def test_anonymous_get_perfil_redirects_to_login_with_next(self):
        response = self.anon.get(self.perfil_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
        self.assertIn("next=", response.url)
        self.assertIn("/misas/perfil/", response.url)
        self.assertNotContains(response, self.user.username, status_code=302)

    def test_login_then_next_returns_perfil(self):
        login_url = reverse("login")
        response = self.anon.post(
            login_url,
            {
                "username": "perfilista",
                "password": "password123",
                "next": self.perfil_url,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.perfil_url)
        follow = self.anon.get(self.perfil_url)
        self.assertEqual(follow.status_code, 200)
        self.assertContains(follow, self.user.username)

    def test_authenticated_get_login_redirects_away_from_form(self):
        self.login()
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(response.url, reverse("login"))

    def test_post_logout_returns_visitor_navbar(self):
        self.login()
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/misas/")
        follow = self.client.get(self.index_url)
        self.assertEqual(follow.status_code, 200)
        self.assertContains(follow, ">Iniciar sesión</a>")
        self.assertNotContains(follow, "Mi perfil")

    def test_get_logout_does_not_log_user_out(self):
        self.login()
        response = self.client.get(reverse("logout"))
        self.assertNotEqual(response.status_code, 302)
        still = self.client.get(self.index_url)
        self.assertContains(still, "Mi perfil")
        self.assertNotContains(still, ">Iniciar sesión</a>")


NOTA_VALIDACION = "La información de este templo aún está sujeta a validación."
NOTA_FESTIVIDADES = (
    "La información y horarios pueden estar sujetos a modificaciones o excepciones "
    "en fechas especiales/festividades."
)
FACEBOOK_URL = "https://www.facebook.com/parroquia"


class FacebookVerificadoTestCase(TestCase):
    """Helpers for Facebook URL + verificación. Do not alter existing ficha/service classes."""

    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="editor",
            password="password123",
        )
        self.staff = user_model.objects.create_user(
            username="admin_staff",
            password="password123",
            is_staff=True,
        )
        self.templo = Templo.objects.create(
            nombre="Parroquia San José",
            direccion="Calle Principal 1",
            alias="San José",
        )
        self.client = Client()
        self.client.force_login(self.user)
        self.staff_client = Client()
        self.staff_client.force_login(self.staff)
        self.nuevo_url = reverse("misas:nuevo_templo")
        self.ficha_url = reverse("misas:templo", args=[self.templo.id])
        self.edit_url = reverse("misas:editar_templo", args=[self.templo.id])
        self.servicios_url = reverse("misas:templo_servicios", args=[self.templo.id])
        self.verificar_url = reverse("misas:verificar_templo", args=[self.templo.id])

    def templo_post_data(self, **overrides):
        data = {
            "nombre": "Parroquia Nueva",
            "direccion": "Avenida Central 10",
            "alias": "",
        }
        data.update(overrides)
        return data

    def edit_post_data(self, **overrides):
        data = {
            "nombre": self.templo.nombre,
            "direccion": self.templo.direccion,
            "alias": self.templo.alias,
            "facebook": self.templo.facebook,
        }
        data.update(overrides)
        return data


class FacebookAltaEdicionTests(FacebookVerificadoTestCase):
    """US1: optional Facebook on create/edit."""

    def test_get_create_and_edit_include_facebook_not_verificado(self):
        create = self.client.get(self.nuevo_url)
        self.assertEqual(create.status_code, 200)
        self.assertContains(create, 'name="facebook"')
        self.assertContains(create, "csrfmiddlewaretoken")
        self.assertNotContains(create, 'name="verificado"')
        edit = self.client.get(self.edit_url)
        self.assertEqual(edit.status_code, 200)
        self.assertContains(edit, 'name="facebook"')
        self.assertContains(edit, "csrfmiddlewaretoken")
        self.assertNotContains(edit, 'name="verificado"')

    def test_post_create_with_facebook_is_unverified(self):
        response = self.client.post(
            self.nuevo_url,
            self.templo_post_data(facebook=FACEBOOK_URL),
        )
        created = Templo.objects.get(nombre="Parroquia Nueva")
        self.assertEqual(created.facebook, FACEBOOK_URL)
        self.assertFalse(created.verificado)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("misas:templo", args=[created.id]))

    def test_post_create_without_facebook_stores_empty(self):
        self.client.post(self.nuevo_url, self.templo_post_data())
        created = Templo.objects.get(nombre="Parroquia Nueva")
        self.assertEqual(created.facebook, "")
        self.assertFalse(created.verificado)

    def test_post_create_scheme_less_facebook_prefixes_https(self):
        self.client.post(
            self.nuevo_url,
            self.templo_post_data(facebook="facebook.com/parroquia"),
        )
        created = Templo.objects.get(nombre="Parroquia Nueva")
        self.assertEqual(created.facebook, "https://facebook.com/parroquia")

    def test_post_create_ignores_client_verificado(self):
        self.client.post(
            self.nuevo_url,
            self.templo_post_data(facebook=FACEBOOK_URL, verificado="1"),
        )
        created = Templo.objects.get(nombre="Parroquia Nueva")
        self.assertFalse(created.verificado)

    def test_post_invalid_facebook_does_not_insert_or_update(self):
        before = Templo.objects.count()
        create = self.client.post(
            self.nuevo_url,
            self.templo_post_data(facebook="no es una url"),
        )
        self.assertEqual(create.status_code, 200)
        self.assertTrue(create.context["form"].errors)
        self.assertEqual(Templo.objects.count(), before)
        self.templo.facebook = FACEBOOK_URL
        self.templo.save()
        edit = self.client.post(
            self.edit_url,
            self.edit_post_data(facebook="no es una url"),
        )
        self.assertEqual(edit.status_code, 200)
        self.assertTrue(edit.context["form"].errors)
        self.templo.refresh_from_db()
        self.assertEqual(self.templo.facebook, FACEBOOK_URL)

    def test_post_edit_changes_only_facebook(self):
        response = self.client.post(
            self.edit_url,
            self.edit_post_data(facebook=FACEBOOK_URL),
        )
        self.assertEqual(response.status_code, 302)
        self.templo.refresh_from_db()
        self.assertEqual(self.templo.facebook, FACEBOOK_URL)
        self.assertEqual(self.templo.nombre, "Parroquia San José")
        self.assertEqual(self.templo.direccion, "Calle Principal 1")
        self.assertEqual(self.templo.alias, "San José")
        self.assertFalse(self.templo.imagen)

    def test_post_edit_empty_facebook_clears_link(self):
        self.templo.facebook = FACEBOOK_URL
        self.templo.save()
        self.client.post(self.edit_url, self.edit_post_data(facebook=""))
        self.templo.refresh_from_db()
        self.assertEqual(self.templo.facebook, "")


class FacebookHeaderDisplayTests(FacebookVerificadoTestCase):
    """US2: shared header shows icon + address when Facebook is set."""

    def test_ficha_and_servicios_show_facebook_link(self):
        self.templo.facebook = FACEBOOK_URL
        self.templo.save()
        anon = Client()
        ficha = anon.get(self.ficha_url)
        self.assertEqual(ficha.status_code, 200)
        self.assertContains(ficha, "bi-facebook")
        self.assertContains(ficha, FACEBOOK_URL)
        self.assertContains(ficha, 'target="_blank"')
        self.assertContains(ficha, 'rel="noopener noreferrer"')
        servicios = self.client.get(self.servicios_url)
        self.assertEqual(servicios.status_code, 200)
        self.assertContains(servicios, "bi-facebook")
        self.assertContains(servicios, FACEBOOK_URL)
        self.assertContains(servicios, 'target="_blank"')
        self.assertContains(servicios, 'rel="noopener noreferrer"')

    def test_empty_facebook_hides_icon_and_href(self):
        anon = Client()
        ficha = anon.get(self.ficha_url)
        self.assertNotContains(ficha, "bi-facebook")
        self.assertNotContains(ficha, 'href=""')
        servicios = self.client.get(self.servicios_url)
        self.assertNotContains(servicios, "bi-facebook")


class VerificarTemploStaffTests(FacebookVerificadoTestCase):
    """US3: staff POST marks or unmarks verificación."""

    def test_staff_post_verifica_and_quita(self):
        mark = self.staff_client.post(self.verificar_url, {"verificado": "1"})
        self.assertEqual(mark.status_code, 302)
        self.assertEqual(mark.url, self.ficha_url)
        self.templo.refresh_from_db()
        self.assertTrue(self.templo.verificado)
        ficha = Client().get(self.ficha_url)
        self.assertContains(ficha, "Verificado")
        servicios = self.client.get(self.servicios_url)
        self.assertContains(servicios, "Verificado")
        unmark = self.staff_client.post(
            self.verificar_url,
            {"verificado": "0", "next": self.servicios_url},
        )
        self.assertEqual(unmark.status_code, 302)
        self.assertEqual(unmark.url, self.servicios_url)
        self.templo.refresh_from_db()
        self.assertFalse(self.templo.verificado)

    def test_get_verificar_is_405(self):
        response = self.staff_client.get(self.verificar_url)
        self.assertEqual(response.status_code, 405)

    def test_unknown_uuid_post_is_404(self):
        url = reverse("misas:verificar_templo", args=[uuid.uuid4()])
        response = self.staff_client.post(url, {"verificado": "1"})
        self.assertEqual(response.status_code, 404)

    def test_verify_post_does_not_mutate_ficha_or_servicios(self):
        self.templo.facebook = FACEBOOK_URL
        self.templo.save()
        self.create_servicio = Servicio.objects.create(
            templo=self.templo,
            tipo_servicio=Servicio.TipoServicio.MISA,
            dia_de_semana=Servicio.DiasSemana.DOMINGO,
            hora_inicio=time(10, 0),
        )
        self.staff_client.post(self.verificar_url, {"verificado": "1"})
        self.templo.refresh_from_db()
        self.assertEqual(self.templo.nombre, "Parroquia San José")
        self.assertEqual(self.templo.facebook, FACEBOOK_URL)
        self.assertEqual(Servicio.objects.filter(templo=self.templo).count(), 1)


class VerificarTemploPermisoTests(FacebookVerificadoTestCase):
    """US4: only staff can change verificado."""

    def test_non_staff_post_is_403(self):
        response = self.client.post(self.verificar_url, {"verificado": "1"})
        self.assertEqual(response.status_code, 403)
        self.templo.refresh_from_db()
        self.assertFalse(self.templo.verificado)

    def test_anonymous_post_redirects_to_login(self):
        anon = Client()
        response = anon.post(self.verificar_url, {"verificado": "1"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
        self.assertIn("next=", response.url)
        self.templo.refresh_from_db()
        self.assertFalse(self.templo.verificado)

    def test_non_staff_does_not_see_verify_buttons(self):
        ficha = self.client.get(self.ficha_url)
        self.assertNotContains(ficha, "Marcar como verificado")
        self.assertNotContains(ficha, "Quitar verificación")
        servicios = self.client.get(self.servicios_url)
        self.assertNotContains(servicios, "Marcar como verificado")
        create = self.client.get(self.nuevo_url)
        edit = self.client.get(self.edit_url)
        self.assertNotContains(create, 'name="verificado"')
        self.assertNotContains(edit, 'name="verificado"')

    def test_anonymous_sees_verificado_without_buttons(self):
        self.templo.verificado = True
        self.templo.save()
        ficha = Client().get(self.ficha_url)
        self.assertContains(ficha, "Verificado")
        self.assertNotContains(ficha, "Marcar como verificado")
        self.assertNotContains(ficha, "Quitar verificación")


class RevocarVerificacionTests(FacebookVerificadoTestCase):
    """US5: valid ficha or servicio save clears verificado."""

    def test_valid_edit_revokes_including_staff(self):
        self.templo.verificado = True
        self.templo.save()
        self.client.post(self.edit_url, self.edit_post_data(nombre="Nombre nuevo"))
        self.templo.refresh_from_db()
        self.assertFalse(self.templo.verificado)
        self.templo.verificado = True
        self.templo.save()
        self.staff_client.post(
            self.edit_url,
            self.edit_post_data(facebook=FACEBOOK_URL),
        )
        self.templo.refresh_from_db()
        self.assertFalse(self.templo.verificado)
        self.assertEqual(self.templo.facebook, FACEBOOK_URL)

    def test_valid_servicio_create_revokes_on_same_response(self):
        self.templo.verificado = True
        self.templo.save()
        response = self.client.post(
            self.servicios_url,
            {
                "tipo_servicio": Servicio.TipoServicio.MISA,
                "dia_de_semana": Servicio.DiasSemana.DOMINGO,
                "hora_inicio": "10:00",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.templo.refresh_from_db()
        self.assertFalse(self.templo.verificado)
        self.assertContains(response, f"{self.templo.nombre}*")
        self.assertContains(response, NOTA_VALIDACION)
        self.assertEqual(Servicio.objects.filter(templo=self.templo).count(), 1)

    def test_invalid_save_does_not_revoke(self):
        self.templo.verificado = True
        self.templo.save()
        edit = self.client.post(
            self.edit_url,
            self.edit_post_data(facebook="no es una url"),
        )
        self.assertEqual(edit.status_code, 200)
        self.templo.refresh_from_db()
        self.assertTrue(self.templo.verificado)
        servicio = self.client.post(
            self.servicios_url,
            {
                "tipo_servicio": Servicio.TipoServicio.MISA,
                "dia_de_semana": Servicio.DiasSemana.DOMINGO,
                "hora_inicio": "11:00",
                "hora_fin": "10:00",
            },
        )
        self.assertEqual(servicio.status_code, 200)
        self.templo.refresh_from_db()
        self.assertTrue(self.templo.verificado)
        self.assertEqual(Servicio.objects.filter(templo=self.templo).count(), 0)

    def test_already_unverified_stays_false(self):
        self.client.post(self.edit_url, self.edit_post_data(nombre="Otro nombre"))
        self.templo.refresh_from_db()
        self.assertFalse(self.templo.verificado)


class AvisosVerificacionTests(FacebookVerificadoTestCase):
    """US6: asterisk, pending note, and festivities note."""

    def test_unverified_shows_asterisk_and_both_notes(self):
        anon = Client()
        ficha = anon.get(self.ficha_url)
        self.assertContains(ficha, f"{self.templo.nombre}*")
        self.assertContains(ficha, NOTA_VALIDACION)
        self.assertContains(ficha, NOTA_FESTIVIDADES)
        servicios = self.client.get(self.servicios_url)
        self.assertContains(servicios, f"{self.templo.nombre}*")
        self.assertContains(servicios, NOTA_VALIDACION)
        self.assertContains(servicios, NOTA_FESTIVIDADES)

    def test_verified_hides_asterisk_and_pending_note(self):
        self.templo.verificado = True
        self.templo.save()
        ficha = Client().get(self.ficha_url)
        self.assertContains(ficha, "Verificado")
        self.assertNotContains(ficha, f"{self.templo.nombre}*")
        self.assertNotContains(ficha, NOTA_VALIDACION)
        self.assertContains(ficha, NOTA_FESTIVIDADES)
        servicios = self.client.get(self.servicios_url)
        self.assertContains(servicios, "Verificado")
        self.assertNotContains(servicios, f"{self.templo.nombre}*")
        self.assertNotContains(servicios, NOTA_VALIDACION)
        self.assertContains(servicios, NOTA_FESTIVIDADES)


SIGNUP_PASSWORD = "ParroquiaClara-2026"
RESET_PASSWORD = "NuevaClaveClara-2026"


def first_mail_url(path_fragment):
    body = mail.outbox[0].body
    match = re.search(rf"https?://[^\s]+{re.escape(path_fragment)}[^\s]+", body)
    if match is None:
        raise AssertionError(f"No URL containing {path_fragment!r} in {body!r}")
    return match.group(0).rstrip(".)")


class CrearCuentaTestCase(TestCase):
    """Shared helpers for public signup, confirmation, and password reset."""

    def setUp(self):
        user_model = get_user_model()
        self.User = user_model
        self.active = user_model.objects.create_user(
            username="activo",
            password="password123",
            email="activo@example.com",
        )
        self.pending = user_model.objects.create_user(
            username="pendiente",
            password="password123",
            email="pendiente@example.com",
        )
        self.pending.is_active = False
        self.pending.save(update_fields=["is_active"])
        self.no_email = user_model.objects.create_user(
            username="sin_correo",
            password="password123",
            email="",
        )
        self.client = Client()
        self.anon = Client()
        self.templo = Templo.objects.create(
            nombre="Parroquia San José",
            direccion="Calle Principal 1",
        )

    def signup_data(self, **overrides):
        data = {
            "username": "nueva_cuenta",
            "email": "nueva@example.com",
            "password1": SIGNUP_PASSWORD,
            "password2": SIGNUP_PASSWORD,
        }
        data.update(overrides)
        return data

    def servicios_url(self):
        return reverse("misas:templo_servicios", args=[self.templo.id])


class LoginEnlacesCuentaTests(CrearCuentaTestCase):
    """US1: login shows Crear cuenta and Olvidé mi contraseña."""

    def test_anonymous_login_shows_spanish_account_links(self):
        response = self.anon.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Crear cuenta")
        self.assertContains(response, reverse("crear_cuenta"))
        self.assertContains(response, "Olvidé mi contraseña")
        self.assertContains(response, reverse("password_reset"))
        self.assertNotContains(response, "Sign up")
        self.assertNotContains(response, "Register")
        self.assertNotContains(response, "Forgot password")

    def test_navbar_does_not_include_signup_or_reset(self):
        response = self.anon.get(reverse("misas:index"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Crear cuenta")
        self.assertNotContains(response, "Olvidé mi contraseña")

    def test_authenticated_login_and_signup_redirect_away(self):
        self.client.force_login(self.active)
        login_response = self.client.get(reverse("login"))
        self.assertEqual(login_response.status_code, 302)
        self.assertNotEqual(login_response.url, reverse("login"))
        signup = self.client.get(reverse("crear_cuenta"))
        self.assertEqual(signup.status_code, 302)
        self.assertEqual(signup.url, "/misas/perfil/")


class AltaCuentaTests(CrearCuentaTestCase):
    """US2: valid signup creates a pending user and sends mail without a session."""

    def test_get_crear_cuenta_shows_spanish_fields(self):
        response = self.anon.get(reverse("crear_cuenta"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Usuario")
        self.assertContains(response, "Correo de contacto")
        self.assertContains(response, "Contraseña")
        self.assertContains(response, "Confirmación de contraseña")
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_valid_signup_creates_pending_user_and_mail(self):
        response = self.anon.post(reverse("crear_cuenta"), self.signup_data())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("cuenta_creada"))
        user = self.User.objects.get(username="nueva_cuenta")
        self.assertEqual(user.email, "nueva@example.com")
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertEqual(user.first_name, "")
        self.assertEqual(user.last_name, "")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["nueva@example.com"])
        confirm_url = first_mail_url("/accounts/confirmar/")
        self.assertIn(confirm_url, mail.outbox[0].body)
        self.assertNotIn(SIGNUP_PASSWORD, mail.outbox[0].body)
        self.assertFalse(self.anon.session.get("_auth_user_id"))
        done = self.anon.get(reverse("cuenta_creada"))
        self.assertEqual(done.status_code, 200)
        self.assertContains(done, "Revisa tu correo")

    def test_pending_credentials_cannot_login_or_edit(self):
        self.anon.post(reverse("crear_cuenta"), self.signup_data())
        self.assertFalse(
            self.anon.login(username="nueva_cuenta", password=SIGNUP_PASSWORD)
        )
        perfil = self.anon.get(reverse("misas:perfil"))
        self.assertEqual(perfil.status_code, 302)
        self.assertIn("/accounts/login/", perfil.url)
        count = Servicio.objects.count()
        editor = self.anon.post(
            self.servicios_url(),
            {
                "tipo_servicio": Servicio.TipoServicio.MISA,
                "dia_de_semana": Servicio.DiasSemana.DOMINGO,
                "hora_inicio": "10:00",
            },
        )
        self.assertEqual(editor.status_code, 302)
        self.assertIn("/accounts/login/", editor.url)
        self.assertEqual(Servicio.objects.count(), count)


class ValidacionAltaTests(CrearCuentaTestCase):
    """US3: invalid signup does not create a user or send mail."""

    def test_empty_fields_show_spanish_errors(self):
        response = self.anon.post(reverse("crear_cuenta"), {})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertFalse(self.User.objects.filter(username="nueva_cuenta").exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_duplicate_username_rejected(self):
        response = self.anon.post(
            reverse("crear_cuenta"),
            self.signup_data(username=self.active.username),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("username", response.context["form"].errors)
        self.assertEqual(self.User.objects.filter(username="activo").count(), 1)
        self.assertEqual(len(mail.outbox), 0)

    def test_invalid_email_rejected(self):
        response = self.anon.post(
            reverse("crear_cuenta"),
            self.signup_data(email="no-es-correo"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.context["form"].errors)
        self.assertFalse(self.User.objects.filter(username="nueva_cuenta").exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_weak_or_mismatched_password_rejected(self):
        cases = [
            {"password1": "corto", "password2": "corto"},
            {"password1": "12345678", "password2": "12345678"},
            {"password1": "password", "password2": "password"},
            {"password1": SIGNUP_PASSWORD, "password2": "OtraClave-2026x"},
        ]
        for extra in cases:
            with self.subTest(extra=extra):
                mail.outbox.clear()
                response = self.anon.post(
                    reverse("crear_cuenta"),
                    self.signup_data(**extra),
                )
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.context["form"].errors)
                self.assertFalse(
                    self.User.objects.filter(username="nueva_cuenta").exists()
                )
                self.assertEqual(len(mail.outbox), 0)

    def test_error_preserves_username_and_email_not_password(self):
        response = self.anon.post(
            reverse("crear_cuenta"),
            self.signup_data(password2="OtraClave-2026x"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "nueva_cuenta")
        self.assertContains(response, "nueva@example.com")
        self.assertNotContains(response, f'value="{SIGNUP_PASSWORD}"')


class ConfirmacionCorreoTests(CrearCuentaTestCase):
    """US4: confirmation link activates the account and signs in."""

    def test_valid_confirm_activates_and_logs_in(self):
        self.anon.post(reverse("crear_cuenta"), self.signup_data())
        confirm_url = first_mail_url("/accounts/confirmar/")
        response = self.anon.get(confirm_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/misas/perfil/")
        user = self.User.objects.get(username="nueva_cuenta")
        self.assertTrue(user.is_active)
        perfil = self.anon.get(reverse("misas:perfil"))
        self.assertEqual(perfil.status_code, 200)
        self.assertContains(perfil, "nueva_cuenta")
        self.assertContains(perfil, "nueva@example.com")
        self.assertNotContains(perfil, SIGNUP_PASSWORD)
        self.assertNotContains(perfil, user.password)

    def test_second_confirm_does_not_deactivate_or_reset_password(self):
        self.anon.post(reverse("crear_cuenta"), self.signup_data())
        confirm_url = first_mail_url("/accounts/confirmar/")
        self.anon.get(confirm_url)
        self.anon.logout()
        second = self.anon.get(confirm_url)
        self.assertEqual(second.status_code, 200)
        user = self.User.objects.get(username="nueva_cuenta")
        self.assertTrue(user.is_active)
        parsed = urlparse(confirm_url)
        uid, token = parsed.path.rstrip("/").split("/")[-2:]
        reset = self.anon.get(
            reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
        )
        if reset.status_code == 302:
            reset = self.anon.get(reset.url)
        self.assertEqual(reset.status_code, 200)
        self.assertFalse(reset.context.get("validlink", True))

    def test_invalid_token_keeps_pending(self):
        self.anon.post(reverse("crear_cuenta"), self.signup_data())
        user = self.User.objects.get(username="nueva_cuenta")
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        response = self.anon.get(
            reverse("confirmar_correo", kwargs={"uidb64": uid, "token": "token-falso"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "no es válido")
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_preexisting_user_still_logs_in_without_confirm(self):
        self.assertTrue(self.client.login(username="activo", password="password123"))
        response = self.client.get(self.servicios_url())
        self.assertEqual(response.status_code, 200)


class RestablecerContrasenaTests(CrearCuentaTestCase):
    """US7: password reset is keyed by username."""

    def test_reset_form_asks_for_username(self):
        response = self.anon.get(reverse("password_reset"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Usuario")
        self.assertContains(response, 'name="username"')
        self.assertNotContains(response, 'name="email"')

    def test_authenticated_reset_redirects_to_perfil(self):
        self.client.force_login(self.active)
        response = self.client.get(reverse("password_reset"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/misas/perfil/")

    def test_active_user_with_email_can_reset(self):
        response = self.anon.post(
            reverse("password_reset"), {"username": self.active.username}
        )
        self.assertEqual(response.status_code, 302)
        done = self.anon.get(response.url)
        self.assertContains(done, "Si la cuenta existe")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.active.email])
        reset_url = first_mail_url("/accounts/reset/")
        page = self.anon.get(reset_url, follow=True)
        self.assertEqual(page.status_code, 200)
        set_path = page.request["PATH_INFO"]
        weak = self.anon.post(
            set_path,
            {"new_password1": "12345678", "new_password2": "12345678"},
        )
        self.assertEqual(weak.status_code, 200)
        self.active.refresh_from_db()
        self.assertTrue(self.active.check_password("password123"))
        saved = self.anon.post(
            set_path,
            {"new_password1": RESET_PASSWORD, "new_password2": RESET_PASSWORD},
        )
        self.assertEqual(saved.status_code, 302)
        self.assertFalse(self.anon.login(username="activo", password="password123"))
        self.assertTrue(self.anon.login(username="activo", password=RESET_PASSWORD))

    def test_pending_unknown_and_no_email_are_generic(self):
        cases = ["pendiente", "no_existe", "sin_correo"]
        for username in cases:
            with self.subTest(username=username):
                mail.outbox.clear()
                response = self.anon.post(
                    reverse("password_reset"), {"username": username}
                )
                self.assertEqual(response.status_code, 302)
                done = self.anon.get(response.url)
                self.assertContains(done, "Si la cuenta existe")
                self.assertEqual(len(mail.outbox), 0)
        self.assertTrue(
            self.User.objects.get(username="pendiente").check_password("password123")
        )

    def test_reset_token_does_not_confirm_pending_user(self):
        self.anon.post(reverse("password_reset"), {"username": self.pending.username})
        self.assertEqual(len(mail.outbox), 0)
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode

        uid = urlsafe_base64_encode(force_bytes(self.pending.pk))
        token = default_token_generator.make_token(self.pending)
        response = self.anon.get(
            reverse("confirmar_correo", kwargs={"uidb64": uid, "token": token})
        )
        self.assertEqual(response.status_code, 200)
        self.pending.refresh_from_db()
        self.assertFalse(self.pending.is_active)


class ReenviarConfirmacionTests(CrearCuentaTestCase):
    """US5: resend confirmation without leaking whether the username exists."""

    def test_resend_pending_sends_new_mail(self):
        self.anon.post(reverse("crear_cuenta"), self.signup_data())
        first_url = first_mail_url("/accounts/confirmar/")
        mail.outbox.clear()
        response = self.anon.post(
            reverse("reenviar_confirmacion"), {"username": "nueva_cuenta"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Si la cuenta existe")
        self.assertEqual(len(mail.outbox), 1)
        new_url = first_mail_url("/accounts/confirmar/")
        confirmed = self.anon.get(new_url)
        self.assertEqual(confirmed.status_code, 302)
        self.anon.logout()
        old = self.anon.get(first_url)
        self.assertEqual(old.status_code, 200)
        user = self.User.objects.get(username="nueva_cuenta")
        self.assertTrue(user.is_active)

    def test_resend_unknown_or_active_is_generic_without_mail(self):
        for username in ("no_existe", self.active.username):
            with self.subTest(username=username):
                mail.outbox.clear()
                response = self.anon.post(
                    reverse("reenviar_confirmacion"), {"username": username}
                )
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Si la cuenta existe")
                self.assertEqual(len(mail.outbox), 0)

    def test_authenticated_resend_redirects(self):
        self.client.force_login(self.active)
        response = self.client.get(reverse("reenviar_confirmacion"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/misas/perfil/")

    def test_pending_login_shows_unconfirmed_and_resend(self):
        response = self.anon.post(
            reverse("login"),
            {"username": self.pending.username, "password": "password123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "aún no está confirmada")
        self.assertContains(response, reverse("reenviar_confirmacion"))


class VolverAlAccesoTests(CrearCuentaTestCase):
    """US6: signup offers a way back to login without creating an account."""

    def test_crear_cuenta_links_to_login(self):
        response = self.anon.get(reverse("crear_cuenta"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("login"))
        self.assertContains(response, "Iniciar sesión")
        follow = self.anon.get(reverse("login"))
        self.assertEqual(follow.status_code, 200)
        self.assertContains(follow, "Iniciar sesión")
        self.assertFalse(self.User.objects.filter(username="nueva_cuenta").exists())


class HorariosListaLegibleTestCase(TestCase):
    """Helpers for readable 12-hour service lists. Do not alter existing test classes."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="editor_horarios",
            password="password123",
        )
        self.templo = Templo.objects.create(
            nombre="Parroquia San José",
            direccion="Calle Principal 1",
        )
        self.anon = Client()
        self.client = Client()
        self.client.force_login(self.user)
        self.ficha_url = reverse("misas:templo", args=[self.templo.id])
        self.editor_url = reverse("misas:templo_servicios", args=[self.templo.id])

    def create_servicio(self, **kwargs):
        defaults = {
            "templo": self.templo,
            "tipo_servicio": Servicio.TipoServicio.MISA,
            "dia_de_semana": Servicio.DiasSemana.DOMINGO,
            "hora_inicio": time(8, 0),
        }
        defaults.update(kwargs)
        return Servicio.objects.create(**defaults)

    def create_same_day_triple(self):
        self.create_servicio(hora_inicio=time(8, 0))
        self.create_servicio(hora_inicio=time(10, 0))
        self.create_servicio(hora_inicio=time(18, 0))


class HorariosFichaTests(HorariosListaLegibleTestCase):
    """US1: public ficha shows comma-separated 12-hour hours, not a Python list."""

    def test_anonymous_ficha_joins_same_day_hours(self):
        self.create_same_day_triple()
        response = self.anon.get(self.ficha_url)
        self.assertEqual(response.status_code, 200)
        horas = next(iter(self.templo.get_servicios().values()))
        joined = ", ".join(next(iter(horas.values())))
        self.assertEqual(
            set(joined.split(", ")), {"8:00 a. m.", "10:00 a. m.", "6:00 p. m."}
        )
        self.assertContains(response, joined)
        self.assertNotContains(response, "['")
        self.assertNotContains(response, "08:00")
        self.assertNotContains(response, "18:00")
        self.assertNotContains(response, "8:00 AM")
        self.assertNotContains(response, "8:00 a.m.")
        self.assertEqual(
            list(
                Servicio.objects.filter(templo=self.templo)
                .order_by("hora_inicio")
                .values_list("hora_inicio", flat=True)
            ),
            [time(8, 0), time(10, 0), time(18, 0)],
        )

    def test_single_hour_has_no_trailing_comma(self):
        self.create_servicio(hora_inicio=time(8, 0))
        response = self.anon.get(self.ficha_url)
        self.assertContains(response, "8:00 a. m.")
        self.assertNotContains(response, "8:00 a. m.,")

    def test_midnight_and_noon_display(self):
        self.create_servicio(
            dia_de_semana=Servicio.DiasSemana.LUNES,
            hora_inicio=time(0, 0),
        )
        self.create_servicio(
            dia_de_semana=Servicio.DiasSemana.MARTES,
            hora_inicio=time(12, 0),
        )
        response = self.anon.get(self.ficha_url)
        self.assertContains(response, "12:00 a. m.")
        self.assertContains(response, "12:00 p. m.")

    def test_unknown_templo_uuid_returns_404(self):
        url = reverse("misas:templo", args=[uuid.uuid4()])
        response = self.anon.get(url)
        self.assertEqual(response.status_code, 404)

    def test_index_listing_does_not_need_day_hour_list(self):
        self.create_same_day_triple()
        response = self.anon.get(reverse("misas:index"))
        self.assertEqual(response.status_code, 200)


class HorariosEditorListaTests(HorariosListaLegibleTestCase):
    """US2: editor lower list matches ficha; create form still posts HH:MM."""

    def test_editor_list_matches_ficha(self):
        self.create_same_day_triple()
        ficha = self.anon.get(self.ficha_url)
        editor = self.client.get(self.editor_url)
        self.assertEqual(editor.status_code, 200)
        horas = next(iter(self.templo.get_servicios().values()))
        joined = ", ".join(next(iter(horas.values())))
        self.assertEqual(
            set(joined.split(", ")), {"8:00 a. m.", "10:00 a. m.", "6:00 p. m."}
        )
        self.assertContains(ficha, joined)
        list_html = editor.content.decode().split("Servicios registrados", 1)[-1]
        self.assertIn(joined, list_html)
        self.assertNotIn("['", list_html)
        self.assertContains(editor, 'name="hora_inicio"')

    def test_empty_templo_keeps_spanish_empty_copy(self):
        response = self.client.get(self.editor_url)
        self.assertEqual(self.templo.get_servicios(), {})
        self.assertContains(
            response, "Aún no hay horarios registrados para este templo."
        )

    def test_post_hora_inicio_still_persists_time(self):
        response = self.client.post(
            self.editor_url,
            {
                "tipo_servicio": Servicio.TipoServicio.MISA,
                "dia_de_semana": Servicio.DiasSemana.DOMINGO,
                "hora_inicio": "10:00",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Servicio.objects.get().hora_inicio, time(10, 0))

    def test_anonymous_editor_redirects_to_login(self):
        response = self.anon.get(self.editor_url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)
        self.assertIn("next=", response.url)
