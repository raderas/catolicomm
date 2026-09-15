# Implementation Plan: Crear cuenta, verificar correo y recuperar contraseña

**Branch**: `005-crear-cuenta` | **Date**: 2026-09-14 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/005-crear-cuenta/spec.md`

## Summary

Public self-registration from the existing Spanish login screen: **Crear cuenta** collects username, contact email, and password (`UserCreationForm` + Django password validators). The new `User` is saved with `is_active=False`, no session is started, and a confirmation email is sent. A signed one-time link activates the account and logs the user in. **Olvidé mi contraseña** is a username-keyed reset (email is not unique) using contrib.auth reset views plus a custom form. Existing staff/preexisting users stay active and keep logging in as today.

## Technical Context

**Language/Version**: Python 3.12, Django 6.1

**Primary Dependencies**: Django `contrib.auth` (`User`, `UserCreationForm`, `AuthenticationForm`, `LoginView`, `PasswordResetView` and related views/urls, `PasswordResetTokenGenerator`, `login()`), Django mail (`MAILERS`), Bootstrap 5 + Bootstrap Icons already in `misas/templates/base.html`

**Storage**: Existing Django `User` table. Confirmation state is `User.is_active`. No new models or migrations.

**Testing**: Django `TestCase` / `Client` in `misas/tests.py` with locmem mail; keep temple/service tests. Browser pass of login links, signup, confirm, inactive login, resend, and reset.

**Target Platform**: Django web app (desktop and mobile browsers)

**Project Type**: Single Django project (`site1`) + `misas` app

**Performance Goals**: Low-traffic parish screens; one extra write on signup; one email send per signup/resend/reset. No new round-trips on public listing/detail.

**Constraints**: Spanish UI (`lang="es"`); CSRF on every POST; secrets and From-address in env; console mail locally, locmem in tests; no custom user model; no allauth; password reset keyed by username; public directory stays public; temple/service write still requires an authenticated **active** user

**Scale/Scope**: Login template links, one signup form/view, confirm + resend routes, override of password-reset form, Spanish auth email/HTML templates, tests. Typical: few editor accounts, not a consumer identity product.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | How this plan complies |
|-----------|--------|------------------------|
| I. Idiomatic Django | Pass | Extend `UserCreationForm`; reuse `LoginView` / `PasswordResetView` / `auth.urls`; `is_active` instead of a profile flag; thin function or generic views; no custom user model, no extra app, no identity framework. |
| II. Critical-path tests | Pass | Signup does not change `Templo`/`Servicio` rows, but login and `login_required` editors are on the critical path. Tests cover: login still works for active users; inactive signup cannot reach perfil/servicios; confirm then editor access; existing temple/service tests stay green. Browser check supplements, does not replace. |
| III. Existing Spanish UI | Pass | Same `base.html` chrome; login card pattern (`card bg-surface`, `btn-gold`, `font-serif`) for signup, “revisa tu correo”, invalid link, reset screens. Copy in Spanish. No new design system. |
| IV. Django security defaults | Pass | CSRF on signup, resend, reset POSTs. Inactive users cannot authenticate, so they cannot mutate temples/services. Tokens are one-time and time-limited. Mail From and secrets stay in env. Generic messages on resend/reset so usernames are not enumerated. |
| V. Community-accurate data | Pass | Does not invent or alter `Templo` / `Servicio`. Profile empty names still show **No registrado**. |
| Stack / YAGNI | Pass | Python 3.12 / Django 6.1, SQLite unchanged, no allauth, no `email_verified` column, no password-change-from-perfil. |

Post-design re-check: same results. Contracts are HTML routes, mail, and settings — not a JSON API. No constitution exceptions; complexity table omitted.

Parish-scoped write (constitution IV “an editor cannot change another parish’s records”) remains the deferred product gap from specs 001–004: any **confirmed** collaborator can still edit any temple. This feature only adds “must be confirmed to authenticate”; it does not introduce a user–templo link.

## Project Structure

### Documentation (this feature)

```text
specs/005-crear-cuenta/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── cuenta.md
└── tasks.md              # /speckit-tasks — not created here
```

### Source Code (repository root)

```text
site1/
├── settings.py                 # DEFAULT_FROM_EMAIL; locmem MAILERS in tests
├── urls.py                     # LoginView form; crear-cuenta / confirmar / reenviar;
                                # PasswordResetView override before auth.urls
misas/
├── forms.py                    # CrearCuentaForm, AutenticacionForm,
                                # UsernamePasswordResetForm, ReenviarConfirmacionForm
├── tokens.py                   # EmailConfirmationTokenGenerator (distinct key_salt)
├── views.py                    # thin signup / cuenta_creada / confirmar / reenviar
├── tests.py                    # signup, mail, confirm, inactive login, reset
└── templates/
    ├── registration/login.html              # + Crear cuenta, Olvidé mi contraseña
    ├── registration/crear_cuenta.html       # new
    ├── registration/cuenta_creada.html      # new
    ├── registration/confirmacion_invalida.html
    ├── registration/reenviar_confirmacion.html
    ├── registration/password_reset_form.html
    ├── registration/password_reset_done.html
    ├── registration/password_reset_confirm.html
    ├── registration/password_reset_complete.html
    ├── registration/password_reset_email.html
    ├── registration/password_reset_subject.txt
    └── registration/confirmacion_email.html (+ subject.txt / optional .txt body)
manage.py
```

**Structure Decision:** Stay in the existing Django monolith. Identity URLs remain under `/accounts/` (alongside login/logout). Forms live in `misas/forms.py`; one small `tokens.py` for a salted generator. Do not add an `accounts` app, a custom user model, or `frontend/`.

## Phase 0 & Phase 1 outputs

- [research.md](./research.md) — `is_active` confirmation, username reset, tokens, mail, tests
- [data-model.md](./data-model.md) — `User` fields, confirmation states, token lifecycle
- [contracts/cuenta.md](./contracts/cuenta.md) — login links, signup, confirm, resend, reset
- [quickstart.md](./quickstart.md) — `manage.py test` and browser pass
