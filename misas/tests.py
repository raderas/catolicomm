import uuid
from datetime import time
from io import BytesIO

from django.contrib.auth import get_user_model
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
        self.assertContains(response, "10:00")
        self.assertContains(response, "18:00")
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
        self.assertIn("10:00", list_html)
        self.assertEqual(list_html.count("10:00"), 1)


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
