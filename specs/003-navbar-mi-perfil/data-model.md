# Data Model: Navegación de sesión y página Mi perfil

This feature does **not** add tables or migrate `Templo` / `Servicio`. Identity stays Django’s built-in `User` (`django.contrib.auth`).

## User (cuenta)

Existing contrib.auth user. Visible on Mi perfil only for the authenticated principal.

| Attribute | Shown? | Rules |
|-----------|--------|--------|
| `username` | yes | Login identifier. Always present for a valid account. Label: **Usuario**. |
| `first_name` | yes | Optional. Empty → show **No registrado**, do not invent a name. Label: **Nombre**. |
| `last_name` | yes | Optional. Empty → **No registrado**. Label: **Apellidos**. |
| `email` | yes | Optional. Empty → **No registrado**. Label: **Correo electrónico**. |
| `date_joined` | yes | Always present. Display localized (project `LANGUAGE_CODE` / timezone). Label: **Fecha de alta**. |
| `password` | **no** | Must not appear (plain, hashed, or hint). |
| `is_staff` / `is_superuser` / `is_active` / `last_login` / groups | **no** | Out of spec. |

**Relationships:** none new. This feature MUST NOT read or write `Templo` or `Servicio`.

**Identity of the page:** there is no profile row and no `user_id` in the URL. The page always binds to `request.user`. Two sessions therefore cannot see each other’s fields without stealing a session.

### Validation / mutation

Mi perfil is read-only. No create, update, or password change. Invalid or missing optional names/email are display concerns only (empty → **No registrado**).

## Session

Django session authentication already in middleware.

| State | Navbar | Mi perfil |
|-------|--------|-----------|
| Anonymous | **Iniciar sesión** visible; **Mi perfil** hidden | GET → redirect to login with `next` |
| Authenticated | **Mi perfil** + person icon; **Iniciar sesión** hidden | GET → 200 with that user’s fields |
| After POST logout | Same as anonymous | Must not remain on perfil; land on Inicio |

Expired / missing session is treated as anonymous.

## Display values (not stored separately)

- Empty text fields: the string **No registrado** (Spanish, explicit).
- Join date: formatted date, not a raw timestamp dump.
- Nav active: **Mi perfil** is the current section only on the profile route; **Inicio** remains the home link.
