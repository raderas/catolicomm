# Research: Navegación de sesión y página Mi perfil

## 1. Session-aware navbar uses the existing auth context, not a new identity stack

**Decision:** In `misas/templates/base.html`, branch on `user.is_authenticated` (already injected by `django.contrib.auth.context_processors.auth`). Anonymous: one nav link **Iniciar sesión** → `{% url 'login' %}` (`/accounts/login/`). Authenticated: one nav link **Mi perfil** with Bootstrap Icon `bi-person-circle` → `misas:perfil`. Never both. Keep **Inicio**. Do not add a permanent Cerrar sesión item to the bar.

**Rationale:** The current `{% url 'misas:login' %}` name does not exist (auth lives under `django.contrib.auth.urls`). FR-002 requires a working login destination. Constitution III: keep the same bar, Spanish copy, cream/gold, existing icon set. Spec assumption: sign-out is on Mi perfil, not a second always-on nav link.

**Alternatives considered:**
- Keep `misas:login` and add a duplicate login route — extra URL; the themed login already exists at `login`.
- Dropdown with profile + logout in the bar — heavier than the spec; logout belongs on Mi perfil (FR-012 / Assumptions).
- English “Login” — forbidden by FR-014 and constitution III.

## 2. Mi perfil is a thin read-only view of Django’s built-in User

**Decision:** Add `@login_required def mi_perfil` in `misas/views.py` that only `render`s `misas/perfil.html`. No form, no `User` model changes, no migration. The template reads `request.user` / `user`: `username`, `first_name`, `last_name`, `email`, `date_joined`. Empty name/email → Spanish **No registrado**. Never output `password`, hashes, `is_staff`, `is_superuser`, or another user’s row. Route: `GET /misas/perfil/` named `misas:perfil` with **no user id in the path**.

**Rationale:** Constitution I: thin view, reuse contrib.auth. FR-007–FR-010 and FR-017: consult own account only; no edit, no password change, no new fields. A URL without a pk makes “view someone else’s profile” impossible without extra code (YAGNI). Auth context processor already exposes `user`, so the view needs no extra context.

**Alternatives considered:**
- Custom user model / profile table — no new attributes in spec.
- `/accounts/profile/` to match Django’s historic default — works, but the directory lives under `/misas/`; a misas route matches Inicio and the rest of the bar.
- `UpdateView` / `ModelForm` — would enable edits the spec forbids.
- Pass `user_id` in the URL and authorize — extra attack surface; rejected.

## 3. Reuse contrib.auth login/logout; set redirect settings; POST-only logout

**Decision:** Keep `LOGIN_URL = "/accounts/login/"`. Set `LOGIN_REDIRECT_URL = "/misas/perfil/"` and `LOGOUT_REDIRECT_URL = "/misas/"`. Enable `LoginView.redirect_authenticated_user=True` by registering `accounts/login/` **before** `include("django.contrib.auth.urls")` (same `LoginView`, same existing `registration/login.html`). On Mi perfil, **Cerrar sesión** is a POST form with CSRF to `{% url 'logout' %}` (Django 5+/6 `LogoutView` does not log out on GET).

**Rationale:** Spec FR-011 (`next` back to perfil), FR-012 (leave perfil after logout; bar returns to Iniciar sesión). Empty `next` today would hit Django’s default `/accounts/profile/`, which 404s. Authenticated GET on login must not show a guest form (spec edge case). POST logout keeps CSRF on (constitution IV). Redirect to Inicio after logout is a public page, so the browser back-button to perfil hits `login_required` again.

**Alternatives considered:**
- Custom auth app or session middleware — forbidden complexity.
- GET logout link — broken / insecure under Django 6.1.
- `LOGOUT_REDIRECT_URL` to login — extra hop; Inicio matches “navigate as visitor”.
- Subclass `LoginView` in `misas` — unnecessary if `as_view(redirect_authenticated_user=True)` is enough.

## 4. Visual language and empty values

**Decision:** Profile page extends `base.html`, uses the same `card bg-surface border-subtle shadow-sm rounded-3` + `font-serif` + `btn-outline-brand` (logout) as login and temple editors. Labels in Spanish: Usuario, Nombre, Apellidos, Correo electrónico, Fecha de alta. Date via `|date` so `LANGUAGE_CODE = es-sv` applies. Mark the Mi perfil nav link active on that route (`active` on `nav-link`). Collapse menu already in `base.html` covers FR-016; no extra JS.

**Rationale:** Constitution III and FR-014–FR-016. `bi-person-circle` is already available from `bootstrap-icons` in `base.html`.

**Alternatives considered:**
- Admin chrome or a new CSS system — forbidden.
- Show `last_login` or staff flags — out of spec; would leak admin posture.

## 5. Tests and browser verification

**Decision:** Add Django `TestCase` / `Client` cases in `misas/tests.py` (new class; do not weaken temple/service tests). Cover navbar on **index** (and at least one other `base.html` screen) for anon vs authenticated, profile GET/redirect/`next`, empty vs filled fields, password absent from HTML, two users isolated, POST logout. Supplement with a browser pass: desktop bar, collapsed menu, login, perfil, logout.

**Rationale:** Constitution II: listing/detail templates share `base.html`, so navbar assertions on those responses are the critical-path evidence for this change. Browser checks supplement; they do not replace tests.

**Alternatives considered:**
- Browser-only verification — not allowed as the sole evidence.
- pytest-django — extra runner; the project uses `manage.py test`.
