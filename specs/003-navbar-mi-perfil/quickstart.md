# Quickstart: Navegación de sesión y página Mi perfil

Validate this feature after implementation. Field rules are in [data-model.md](./data-model.md); HTTP/HTML behavior is in [contracts/mi-perfil.md](./contracts/mi-perfil.md).

## Prerequisites

- Python 3.12, project virtualenv, dependencies from `requirements.txt`
- Env vars already used by the app (`DJANGO_SECRET_KEY`, database settings)
- At least one Django user (`python manage.py createsuperuser` if needed), preferably with some of nombre / apellidos / correo filled and another with those empty

## Automated checks

From the repo root:

```bash
python manage.py test misas
```

Expect existing temple/service tests to keep passing, plus coverage of:

- Anonymous GET of a `base.html` page (at least `misas:index`) → HTML contains **Iniciar sesión** and `/accounts/login/`; does **not** contain **Mi perfil** or the English nav label **Login**
- Authenticated GET of the same page → HTML contains **Mi perfil** and a person-style icon class; does **not** contain a navbar **Iniciar sesión**
- Anonymous GET `/misas/perfil/` → `302` to `/accounts/login/` with `next` pointing at perfil; body does not show account fields
- Login POST with `next` to perfil → lands on perfil `200`
- Authenticated GET perfil → `200`; shows that user’s `username` and `date_joined`; shows first name / last name / email when set; shows **No registrado** when those are empty
- Authenticated GET perfil → response does **not** contain the user’s password or hash; no save/edit form for those fields
- Second authenticated user GET perfil → sees own username, not the first user’s
- Authenticated POST `/accounts/logout/` with CSRF → `302` to `/misas/`; follow-up GET index shows **Iniciar sesión** again
- Authenticated GET `/accounts/login/` → redirect away from the guest form

## Manual browser pass (required for UI)

1. Sign out. Open Inicio (and a temple ficha). Confirm the bar shows **Inicio** and **Iniciar sesión**, not **Mi perfil** and not **Login**. Follow **Iniciar sesión** to the existing Spanish login card.
2. Narrow the viewport until the bar collapses; open the menu; confirm **Iniciar sesión** is still there.
3. Sign in. Confirm the bar now shows **Mi perfil** with a person icon and no **Iniciar sesión**. Follow **Mi perfil**; confirm your usuario, nombre, apellidos, correo (or **No registrado**), and fecha de alta. Confirm no password and no edit fields.
4. Confirm the page uses the same cream/gold card and bar as the directory; **Mi perfil** looks active in the bar.
5. Open `/accounts/login/` while still signed in; confirm you are not asked to log in again as a guest.
6. Click **Cerrar sesión**. Confirm you land on Inicio as a visitor (**Iniciar sesión** in the bar). Using back to perfil should ask you to sign in again.
7. Repeat the collapsed-menu check while signed in (**Mi perfil** visible in the menu).

## Done when

Tests above pass and the browser pass matches the spec (session-aware bar, read-only own profile, login wall, logout).
