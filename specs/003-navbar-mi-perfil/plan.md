# Implementation Plan: Navegación de sesión y página Mi perfil

**Branch**: `003-navbar-mi-perfil` | **Date**: 2026-09-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-navbar-mi-perfil/spec.md`

## Summary

Make the shared navbar session-aware: anonymous visitors get a working **Iniciar sesión** link to the existing `/accounts/login/` screen; authenticated users get **Mi perfil** with a person icon. Add a read-only `/misas/perfil/` page that shows the signed-in Django user’s username, names, email, and join date (empty optional fields → **No registrado**), plus a CSRF POST **Cerrar sesión**. No new user fields, no profile edit, no temple/service changes.

## Technical Context

**Language/Version**: Python 3.12, Django 6.1

**Primary Dependencies**: Django (`login_required`, `contrib.auth` views/urls, auth context processor), Bootstrap 5 + Bootstrap Icons already in `misas/templates/base.html`

**Storage**: Existing Django `User` table. No new models or migrations. Sessions as already configured.

**Testing**: Django `TestCase` / `Client` in `misas/tests.py` (keep temple/service tests), plus a browser pass of navbar, perfil, login `next`, collapsed menu, and logout

**Target Platform**: Django web app (desktop and mobile browsers)

**Project Type**: Single Django project (`site1`) + `misas` app

**Performance Goals**: Low-traffic parish screens; one extra GET for perfil; navbar is the same shared template (no extra round-trip)

**Constraints**: Spanish UI (`lang="es"`); CSRF stays on (especially logout POST); no new design system; views stay thin; no profile edit, password change, registration, or User model extension; public directory remains public

**Scale/Scope**: One navbar branch, one route/template, two auth redirect settings, login view flag, tests. Typical: few editor accounts, not a social profile network.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | How this plan complies |
|-----------|--------|------------------------|
| I. Idiomatic Django | Pass | Thin `@login_required` function view; reuse `User` and `contrib.auth.urls`; `LoginView.as_view(redirect_authenticated_user=True)` only. No custom user model, no service layer, no extra app. |
| II. Critical-path tests | Pass | Navbar is on listing/detail via `base.html`: tests assert anon vs auth markup on at least index. New tests for perfil GET/redirect/isolation/logout. Browser check supplements, does not replace. Existing temple/service tests stay green. |
| III. Existing Spanish UI | Pass | Same `navbar` in `base.html`; **Inicio** kept; **Login** → **Iniciar sesión**; perfil uses `card` / cream-gold / `btn-outline-brand` / `bi-person-circle`. No new design system. Changing the session links is the feature, not a second nav chrome. |
| IV. Django security defaults | Pass | CSRF remains; logout is POST. Perfil is authenticated read of `request.user` only (no user id in the URL). Public mass/temple consult stays unauthenticated. This feature does not mutate temple/service rows, so parish-write authorization is N/A here. Secrets stay in env. |
| V. Community-accurate data | Pass | Does not invent or alter `Templo` / `Servicio`. Profile empty names/email show **No registrado**, not fabricated values. |
| Stack / YAGNI | Pass | Python 3.12 / Django 6.1. No new persistence, no profile microservice, no JS framework. |

Post-design re-check: same results. Contracts are HTML routes and settings, not a JSON API. No constitution exceptions; complexity table omitted.

## Project Structure

### Documentation (this feature)

```text
specs/003-navbar-mi-perfil/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── mi-perfil.md
└── tasks.md              # /speckit-tasks — not created here
```

### Source Code (repository root)

```text
site1/
├── settings.py                 # LOGIN_REDIRECT_URL, LOGOUT_REDIRECT_URL
├── urls.py                     # LoginView redirect_authenticated_user before auth.urls
misas/
├── views.py                    # login_required mi_perfil
├── urls.py                     # perfil route
├── tests.py                    # navbar / perfil / logout cases
└── templates/
    ├── base.html               # session-aware nav links
    ├── misas/perfil.html       # new read-only profile + logout form
    └── registration/login.html # unchanged template; still used by LoginView
manage.py
```

**Structure Decision:** Stay in the existing Django monolith. Touch the shared navbar, one view/route/template, and auth redirect settings. Do not add `frontend/`, a accounts app, or a User profile model.

## Phase 0 & Phase 1 outputs

- [research.md](./research.md) — navbar auth branch, thin perfil view, login/logout redirects, UI, tests
- [data-model.md](./data-model.md) — existing `User` fields shown vs hidden; session states
- [contracts/mi-perfil.md](./contracts/mi-perfil.md) — navbar, GET perfil, login, POST logout, settings
- [quickstart.md](./quickstart.md) — `manage.py test` and browser pass
