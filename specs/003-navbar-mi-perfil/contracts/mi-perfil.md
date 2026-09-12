# Contract: Barra de sesión y Mi perfil

Internal Django HTML contract. Not a public JSON API.

## Shared navbar (`base.html` on every misas screen)

Rendered on all templates that extend `base.html` (index, ficha, editors, login, perfil).

| Session | Must include | Must not include |
|---------|--------------|------------------|
| Anonymous | Link text **Iniciar sesión** pointing at `{% url 'login' %}` (`/accounts/login/`) | **Mi perfil**; English **Login**; a broken `misas:login` URL |
| Authenticated | Link text **Mi perfil** plus person/account icon (`bi-person-circle`), pointing at `misas:perfil` | **Iniciar sesión** in the bar |

**Inicio** remains and points at `misas:index`. Both session links stay inside the existing collapse (`#navContent`) for small viewports.

On `misas:perfil`, the Mi perfil nav link SHOULD carry the `active` state.

## Routes

| Method | Path | Name | Auth | Result |
|--------|------|------|------|--------|
| GET | `/misas/perfil/` | `misas:perfil` | Anonymous | `302` to `/accounts/login/` with `next` pointing at this URL. Body MUST NOT include another user’s (or any) profile fields. |
| GET | `/misas/perfil/` | `misas:perfil` | Authenticated | `200`. Spanish read-only page: Usuario, Nombre, Apellidos, Correo electrónico, Fecha de alta for **this** user. Empty optional fields → **No registrado**. MUST include POST **Cerrar sesión**. MUST NOT include password (or hash). MUST NOT include an edit/save form. Same card / cream-gold language as the directory. |
| POST | `/misas/perfil/` | `misas:perfil` | any | Not used. MUST NOT update the `User`. |
| GET | `/accounts/login/` | `login` | Anonymous | `200`. Existing Spanish sign-in. After success, honor `next` if present; otherwise `LOGIN_REDIRECT_URL` (`/misas/perfil/`). |
| GET | `/accounts/login/` | `login` | Authenticated | `302` away from the login form (`redirect_authenticated_user`); land on `next` if safe, else `/misas/perfil/`. MUST NOT re-display the guest form. |
| POST | `/accounts/login/` | `login` | Anonymous | Existing auth. Valid credentials + `next=/misas/perfil/` → `302` to perfil. |
| POST | `/accounts/logout/` | `logout` | Authenticated | CSRF required. Invalidate session. `302` to `LOGOUT_REDIRECT_URL` (`/misas/`). |
| GET | `/accounts/logout/` | `logout` | any | MUST NOT log the user out (Django 6 POST-only logout). |

`LOGIN_URL` stays `/accounts/login/`.

## Profile page body (GET authenticated)

No POST body. Display mapping:

| Label | Source | Empty |
|-------|--------|-------|
| Usuario | `user.username` | N/A (always set) |
| Nombre | `user.first_name` | **No registrado** |
| Apellidos | `user.last_name` | **No registrado** |
| Correo electrónico | `user.email` | **No registrado** |
| Fecha de alta | `user.date_joined` | N/A (always set); localized date |

Logout control:

| Field | Required | Notes |
|-------|----------|--------|
| `csrfmiddlewaretoken` | yes | POST to `logout` |
| (no other fields) | | Button label **Cerrar sesión** |

## Isolation

| Situation | Result |
|-----------|--------|
| User A authenticated GET perfil | Only A’s `username` / names / email / join date |
| User B authenticated GET perfil | Only B’s fields; A’s username MUST NOT appear |
| User A’s password string or hash | MUST NOT appear in HTML |
| Anonymous GET perfil | Login redirect; no account fields |

## Settings contract

| Setting | Value |
|---------|--------|
| `LOGIN_URL` | `/accounts/login/` (unchanged) |
| `LOGIN_REDIRECT_URL` | `/misas/perfil/` |
| `LOGOUT_REDIRECT_URL` | `/misas/` |

## Out of scope (MUST NOT appear)

Edit profile, change password, registration, staff flags, temple lists, schedule data changes, a second always-visible logout link in the navbar.
