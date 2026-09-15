---
description: "Task list for crear cuenta, verificar correo y recuperar contraseña"
---

# Tasks: Crear cuenta, verificar correo y recuperar contraseña

**Input**: Design documents from `/specs/005-crear-cuenta/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included. Spec independent tests, constitution II (`login_required` temple/service editors), and `quickstart.md` automated checks. Write tests first and confirm they fail before implementation. Do not weaken existing temple/service or navbar/perfil coverage in `misas/tests.py`. Use `Client.login()` (not `force_login`) when asserting that pending (`is_active=False`) users cannot authenticate.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Existing Django monolith: `site1/` project, `misas/` app (not `src/`). Identity URLs stay under `/accounts/` in `site1/urls.py`.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Shared test helpers and test mail. The Django project, `contrib.auth` `User`, and `/accounts/login/` already exist. No new packages. No `User` model changes and no migrations.

- [X] T001 Add a new `TestCase` helper class in `misas/tests.py` (do not change behavior of existing temple/service/navbar classes) that builds: an **active** `User` (`is_active=True`, `email` set, `is_staff=False`); a **pending** `User` (`is_active=False`, `email` set); an active user with empty `email`; anonymous `Client`. Include helpers to POST signup fields. MUST NOT use `force_login` for pending-auth assertions later
- [X] T002 [P] In `site1/settings.py`, set `DEFAULT_FROM_EMAIL` from the environment. In the existing `if "test" in sys.argv` block, set `MAILERS["default"]["BACKEND"]` to `django.core.mail.backends.locmem.EmailBackend`. Keep console mail for non-test runs. No secrets in source

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Named signup route so login can link to a real destination. Token generator for later confirmation. Stub GET only — do **not** create users, send mail, or confirm yet.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 [P] Add `EmailConfirmationTokenGenerator(PasswordResetTokenGenerator)` in `misas/tokens.py` with a distinct `key_salt` (e.g. `"misas.email_confirmation"`). Export `email_confirmation_token_generator`. Do not send mail yet
- [X] T004 [P] Add thin `crear_cuenta` in `misas/views.py` that `render`s `registration/crear_cuenta.html` on GET. No `User` insert. No `login()`. No `login_required`
- [X] T005 [P] In `site1/urls.py`, add `accounts/crear-cuenta/` named `crear_cuenta` pointing at `misas.views.crear_cuenta`. Keep `LoginView.as_view(redirect_authenticated_user=True)` **before** `include("django.contrib.auth.urls")`
- [X] T006 [P] Create stub `misas/templates/registration/crear_cuenta.html` extending `misas/templates/base.html` with `{% block title %}Crear cuenta{% endblock %}` and the same cream/gold `card bg-surface border-subtle shadow-sm rounded-3` shell as `misas/templates/registration/login.html`. No form fields yet (US2)

**Checkpoint**: Foundation ready — `GET /accounts/crear-cuenta/` is `200` for anonymous; login HTML still has no **Crear cuenta** / **Olvidé mi contraseña**; no new `User` rows from this path

---

## Phase 3: User Story 1 - Encontrar “Crear cuenta” y “Olvidé mi contraseña” en el acceso (Priority: P1) 🎯 MVP

**Goal**: Anonymous login card shows Spanish **Crear cuenta** and **Olvidé mi contraseña** to real routes. Those links are not in the navbar. Authenticated visitors are not shown guest signup/reset.

**Independent Test**: Signed-out GET `/accounts/login/` shows both links; **Crear cuenta** opens `/accounts/crear-cuenta/`; **Olvidé mi contraseña** opens `/accounts/password_reset/`. Navbar on Inicio still has only **Iniciar sesión**. Signed-in GET of login or crear-cuenta does not show the guest alta.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T007 [US1] Add failing `Client` tests in `misas/tests.py`: anonymous GET `login` is `200` and contains **Crear cuenta**, `reverse("crear_cuenta")` (`/accounts/crear-cuenta/`), **Olvidé mi contraseña**, and `reverse("password_reset")` (`/accounts/password_reset/`); MUST NOT contain **Sign up**, **Register**, or **Forgot password**; anonymous GET `misas:index` MUST NOT contain **Crear cuenta** or **Olvidé mi contraseña** in the navbar; authenticated GET `login` stays `302` away from the guest form; authenticated GET `crear_cuenta` is `302` to `/misas/perfil/` (MUST NOT re-display the alta)

### Implementation for User Story 1

- [X] T008 [P] [US1] In `misas/templates/registration/login.html`, below the submit button, add **Crear cuenta** → `{% url 'crear_cuenta' %}` and **Olvidé mi contraseña** → `{% url 'password_reset' %}`. Keep `{% csrf_token %}` and **Iniciar sesión**. Do not add those links to `misas/templates/base.html`
- [X] T009 [P] [US1] In `misas/views.py`, if `request.user.is_authenticated` on `crear_cuenta`, `redirect` to `LOGIN_REDIRECT_URL` (`/misas/perfil/`). Anonymous GET still `200` stub

**Checkpoint**: Visitors can find both actions from login; signed-in users skip the alta. Signup POST still does nothing (US2)

---

## Phase 4: User Story 2 - Registrar una cuenta y esperar el correo de confirmación (Priority: P1)

**Goal**: Valid POST creates a contrib.auth `User` with `username` required/unique (letters, digits, `@ . + - _`; max length 150), `email` required/valid format/**not unique**, hashed password, `is_active=False`, `is_staff=False`, `is_superuser=False`, empty `first_name`/`last_name`. No session. One confirmation email. Spanish “revisa tu correo” page. Pending credentials cannot reach perfil or temple editors.

**Independent Test**: POST valid alta → pending user + one mail + still a visitor. `Client.login` with those credentials fails. GET perfil and POST servicios redirect to login; no new `Servicio`.

### Tests for User Story 2

- [X] T010 [US2] Add failing tests in `misas/tests.py`: GET `crear_cuenta` (anon) is `200` with labels **Usuario**, **Correo de contacto**, contraseña and confirmación, plus CSRF; valid POST creates `User` with that `username` and `email`, `is_active is False`, `is_staff is False`, `is_superuser is False`, empty names; `len(mail.outbox) == 1` to that email containing an absolute `confirmar_correo` URL (may 404 until US4); client is **not** authenticated; `302` to `cuenta_creada`; GET `cuenta_creada` is `200` with Spanish “revisa tu correo”; `Client.login` pending → `False`; anonymous GET `misas:perfil` still login redirect; pending POST `misas:templo_servicios` is login redirect and MUST NOT insert `Servicio`

### Implementation for User Story 2

- [X] T011 [P] [US2] Add `CrearCuentaForm(UserCreationForm)` in `misas/forms.py`: required `EmailField` label **Correo de contacto** (valid format, **not unique**); `username` required, unique, charset letters/digits/`@ . + - _`, max length 150; `password1`/`password2` with existing `AUTH_PASSWORD_VALIDATORS` (min 8, not similar to username/email, not common, not only numeric). `save()` sets `email`, `is_active=False`, `is_staff=False`, `is_superuser=False`. Spanish labels
- [X] T012 [P] [US2] Add Spanish confirmation mail templates under `misas/templates/registration/` (`confirmacion_email.html` and subject `.txt`; optional `.txt` body). MUST include the absolute `confirmar_correo` link. MUST NOT include the password
- [X] T013 [US2] Wire POST on `crear_cuenta` in `misas/views.py`: invalid wait for US3; valid → `form.save()`, send confirmation mail via `email_confirmation_token_generator` + `uidb64`, **do not** `login()`, `redirect` to `cuenta_creada`. Add `cuenta_creada` view + `accounts/cuenta-creada/` named `cuenta_creada` in `site1/urls.py`
- [X] T014 [US2] Replace the stub in `misas/templates/registration/crear_cuenta.html` with the CSRF form (`username`, `email`, `password1`, `password2`, `form-control`, `btn btn-gold`) matching `login.html`. Add `misas/templates/registration/cuenta_creada.html` (revisa tu correo, same card). Do not add “volver a iniciar sesión” yet if that is US6; do not add resend yet (US5)

**Checkpoint**: Valid alta creates a pending user and sends mail; the person is still a visitor. Confirm GET may still 404 (US4). Validation copy is US3

---

## Phase 5: User Story 3 - Recibir errores claros si el alta no es válida (Priority: P1)

**Goal**: Invalid alta does not create a user or send mail. Spanish errors. Username and email preserved; passwords not redisplayed.

**Independent Test**: Empty fields, duplicate username, invalid email, weak password, mismatched confirmation → Spanish errors, zero new users, `outbox` empty. A later valid POST still succeeds.

### Tests for User Story 3

- [X] T015 [US3] Add failing tests in `misas/tests.py`: POST crear-cuenta with empty `username`/`email`/`password1` → `200`, Spanish missing-field errors, no `User`, `len(mail.outbox) == 0`; duplicate `username` → Spanish unavailable, no second row; invalid email (no `@`) → Spanish error, no user; password shorter than 8, only numeric, too common, or too similar to username/email → Spanish reason, no user; `password2` ≠ `password1` → Spanish mismatch, no user; after an error, response still contains the posted `username` and `email` and MUST NOT redisplay `password1`/`password2` values

### Implementation for User Story 3

- [X] T016 [US3] In `misas/forms.py` and `misas/templates/registration/crear_cuenta.html`, surface `form.non_field_errors` and field errors with `invalid-feedback d-block` (same pattern as `login.html`). Preserve `username` and `email` on invalid POST. Leave password widgets empty. Invalid POST MUST NOT call save/send-mail. CSRF remains

**Checkpoint**: Invalid altas are explained in Spanish and leave no pending user. Happy path from US2 still green

---

## Phase 6: User Story 4 - Confirmar el correo y activar la cuenta (Priority: P1)

**Goal**: Valid confirmation GET sets `is_active=True`, `login()`s the user, redirects to `/misas/perfil/`. Invalid/expired/reused links show Spanish failure and do not activate. Confirm tokens MUST NOT work on password-reset confirm. Preexisting active users still log in without this mail.

**Independent Test**: Follow the signup mail link → identified on Mi perfil (usuario + correo, no password). Logout and login with the same password works. Bad link does not activate. Existing `create_user` editor still reaches servicios.

### Tests for User Story 4

- [X] T017 [US4] Add failing tests in `misas/tests.py`: GET valid `confirmar_correo` uid/token for a pending user → `is_active is True`, client authenticated, `302` to `/misas/perfil/`, perfil `200` shows `username` and `email`, MUST NOT contain password/hash; second GET of the same URL does not deactivate and MUST NOT accept the token on `password_reset_confirm`; bad/expired token → `200` Spanish invalid page, user stays pending; already-active user (admin/`create_user`) GET `login` POST still authenticates and GET `misas:templo_servicios` is `200` without confirmation mail

### Implementation for User Story 4

- [X] T018 [P] [US4] Add `confirmar_correo` in `misas/views.py` and `accounts/confirmar/<uidb64>/<token>/` named `confirmar_correo` in `site1/urls.py`. Pending + valid `email_confirmation_token_generator` → `is_active=True`, `login(..., backend=ModelBackend)`, `302` to `/misas/perfil/`. Already active → Spanish “ya confirmada” and path to login/perfil (do not set `is_active=False`). Invalid uid/token → `200` invalid template. MUST NOT use `default_token_generator` here
- [X] T019 [P] [US4] Add `misas/templates/registration/confirmacion_invalida.html` (Spanish, cream/gold card, path to reenviar can wait for US5). CSRF not required on GET confirm

**Checkpoint**: Confirmation activates and signs in. Password reset still uses Django’s email form until US7. Resend is US5

---

## Phase 7: User Story 7 - Recuperar la contraseña desde el acceso (Priority: P1)

**Goal**: Reset is keyed by **Usuario** (not email). Generic visitor copy always. Mail only for **confirmed** (`is_active=True`) users with non-empty `email`. New password uses the same validators + confirmation; old password stops working; no auto-login. Pending/unknown/no-email: generic page, no useful mail.

**Independent Test**: From login, **Olvidé mi contraseña**, enter a confirmed username with email, open the link, set a valid password, sign in with the new one; old fails. Pending username: same generic page, no mail.

### Tests for User Story 7

- [X] T020 [US7] Add failing tests in `misas/tests.py`: anonymous GET `password_reset` is `200` with **Usuario** (MUST NOT require `email` as the lookup field); authenticated GET `password_reset` is `302` to perfil; POST username of active+email → generic done copy, `len(mail.outbox) == 1` to that email with `password_reset_confirm` URL; POST that confirm with valid matching passwords → old password `Client.login` False, new password True; weak/mismatched new password → Spanish error, old still works; POST pending username, unknown username, or active with empty email → **same** generic visitor copy, no (useful) mail, password unchanged; reset token MUST NOT activate a pending user via `confirmar_correo`

### Implementation for User Story 7

- [X] T021 [P] [US7] Add `UsernamePasswordResetForm` in `misas/forms.py` with `username` (login identifier). `save()` sends the contrib.auth reset mail **only** if that `User` exists, `is_active=True`, and `email` is non-empty. Do not reveal those cases to the caller
- [X] T022 [P] [US7] In `site1/urls.py`, register `PasswordResetView.as_view(form_class=UsernamePasswordResetForm, ...)` on `accounts/password_reset/` **before** `include("django.contrib.auth.urls")`. Authenticated GET/POST → `302` to `/misas/perfil/`. Keep `password_reset_done` / `password_reset_confirm` / `password_reset_complete` from `auth.urls`
- [X] T023 [US7] Add Spanish cream/gold templates: `misas/templates/registration/password_reset_form.html` (Usuario + CSRF), `password_reset_done.html` (generic copy), `password_reset_confirm.html` (`password1`/`password2`, same validators), `password_reset_complete.html` (link to **Iniciar sesión**, no auto-login), `password_reset_email.html` + `password_reset_subject.txt` (Spanish, reset URL, MUST NOT include password)

**Checkpoint**: Username-keyed reset works for confirmed accounts. Signup/confirm still green. Resend confirmation is US5

---

## Phase 8: User Story 5 - Reenviar el correo de confirmación (Priority: P2)

**Goal**: Resend by **Usuario** with always-generic visitor copy. Mail only when pending + email. New link confirms; old confirmation token must not confirm. Inactive login shows Spanish unconfirmed copy plus resend path.

**Independent Test**: Request resend for a pending user → new mail, new link activates. Unknown/already-confirmed username → same generic page, no third-party mail. Pending login shows unconfirmed + resend.

### Tests for User Story 5

- [X] T024 [US5] Add failing tests in `misas/tests.py`: GET/POST `reenviar_confirmacion` anonymous; POST pending username → generic success, one new confirmation mail; new token GET confirms; old token GET does not confirm (or is invalid after the new one is used / after activation); POST unknown or already-active username → **same** generic copy, `outbox` empty (or no mail to a third party); authenticated GET resend → `302` perfil; POST `login` with pending credentials contains Spanish unconfirmed wording and a path to `reenviar_confirmacion`

### Implementation for User Story 5

- [X] T025 [US5] Add `ReenviarConfirmacionForm` in `misas/forms.py` (`username` only) and `reenviar_confirmacion` view in `misas/views.py` plus `accounts/reenviar-confirmacion/` named `reenviar_confirmacion` in `site1/urls.py`. POST always generic success. Send mail only if pending + email. Authenticated → perfil
- [X] T026 [US5] Add `misas/templates/registration/reenviar_confirmacion.html`. Link resend from `cuenta_creada.html` and `confirmacion_invalida.html`. Subclass `AuthenticationForm` as `AutenticacionForm` in `misas/forms.py` with Spanish `inactive` error and resend hint; pass `authentication_form=` on `LoginView` in `site1/urls.py`; show the error on `misas/templates/registration/login.html`

**Checkpoint**: Lost/expired confirmation mail can be retried without leaking whether a username exists

---

## Phase 9: User Story 6 - Volver al acceso desde el alta (Priority: P2)

**Goal**: Signup screen offers Spanish **Iniciar sesión** (or equivalent) back to login without creating an account.

**Independent Test**: From crear-cuenta, use the back action → login form; no new `User`.

### Tests for User Story 6

- [X] T027 [US6] Add failing tests in `misas/tests.py`: GET `crear_cuenta` contains a link to `reverse("login")` with Spanish access copy (not only the navbar); following it is `200` login; no extra `User` from GET

### Implementation for User Story 6

- [X] T028 [US6] In `misas/templates/registration/crear_cuenta.html`, add a Spanish action back to `{% url 'login' %}` (same card). MUST NOT submit the alta. Keep **Crear cuenta** submit distinct

**Checkpoint**: Visitor can leave signup without registering. US1–US5 and US7 still pass

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Full quickstart validation, Spanish UI, CSRF, mail safety, no scope creep

- [X] T029 Run `python manage.py test misas` from repo root until US1–US7 cases in `specs/005-crear-cuenta/quickstart.md` pass (existing temple/service and navbar/perfil tests MUST stay green)
- [X] T030 Browser-pass `specs/005-crear-cuenta/quickstart.md`: login links (not in navbar), signup, invalid errors, console confirmation link, Mi perfil, reused link, collapsed menu, username reset, preexisting staff login without confirm
- [X] T031 Confirm out of scope: no custom `User` / `email_verified` column, no unique email constraint, no navbar **Crear cuenta**, no password change on `misas/templates/misas/perfil.html`, no staff flags at signup, no password in any `misas/templates/registration/` email; `{% csrf_token %}` on every POST form; confirmation token rejected by reset-confirm and the reverse
- [X] T032 Run `pre-commit run ruff-check --all-files` and `pre-commit run ruff-format --all-files` after Python edits; fix reported issues in `misas/forms.py`, `misas/views.py`, `misas/tokens.py`, `misas/tests.py`, `site1/settings.py`, `site1/urls.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational
  - Sequential for one implementer: US1 → US2 → US3 → US4 → US7 → US5 → US6 (shared `login.html` / `crear_cuenta.html` / `views.py` / `forms.py` / `site1/urls.py`)
  - P1 stories (US1, US2, US3, US4, US7) before P2 (US5, US6)
- **Polish (Phase 10)**: Depends on US1–US7 complete

### User Story Dependencies

- **User Story 1 (P1)**: After Phase 2 stub `crear_cuenta` route. MVP. Login links only. `password_reset` URL already exists from `auth.urls` (email-based until US7)
- **User Story 2 (P1)**: After US1 so visitors can reach the form. Creates pending `User` + mail. Confirm URL in the mail may 404 until US4
- **User Story 3 (P1)**: After US2 form exists. Invalid POST paths on the same form
- **User Story 4 (P1)**: After US2 mail contains uid/token. Activates pending users. Independently testable with a factory pending user if mail is built in the test
- **User Story 7 (P1)**: After Phase 2. Can start after US1 (link already points at `password_reset`). Safer after US4 so confirm vs reset token isolation tests have `confirmar_correo`. Do **not** require US5
- **User Story 5 (P2)**: After US4 (needs working confirm tokens). Adds resend + inactive login copy
- **User Story 6 (P2)**: After US2 template exists. Back link only

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Forms before views that save; views before templates that bind widget ids if needed
- Story complete before next priority if working sequentially

### Parallel Opportunities

- T002 and T003 in parallel after T001 (`site1/settings.py` vs `misas/tokens.py`)
- T004, T005, T006 in parallel (views / urls / stub template)
- T008 and T009 in parallel after T007 (`login.html` vs `views.py`)
- T011 and T012 in parallel after T010 (`forms.py` vs email templates)
- T018 and T019 in parallel after T017 (view/urls vs invalid template)
- T021 and T022 in parallel after T020 (`forms.py` vs `site1/urls.py`) — T023 templates after or with T022
- Do **not** parallelize T025/T026 (shared `misas/forms.py` and `site1/urls.py`)

---

## Parallel Example: Foundational

```bash
# After T001–T002 (or T002 in parallel with T003):
Task: "Add EmailConfirmationTokenGenerator in misas/tokens.py"
Task: "Add stub crear_cuenta in misas/views.py"
Task: "Add accounts/crear-cuenta/ in site1/urls.py"
Task: "Create stub misas/templates/registration/crear_cuenta.html"
```

## Parallel Example: User Story 2

```bash
# After T010 tests fail:
Task: "Add CrearCuentaForm in misas/forms.py"
Task: "Add confirmation email templates under misas/templates/registration/"
```

## Parallel Example: User Story 7

```bash
# After T020 tests fail:
Task: "Add UsernamePasswordResetForm in misas/forms.py"
Task: "Override PasswordResetView in site1/urls.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: login shows working **Crear cuenta** and **Olvidé mi contraseña**; navbar unchanged
5. Continue US2–US4 and US7 before calling the feature done (pending signup, errors, confirm, and reset are also P1)

### Incremental Delivery

1. Setup + Foundational → test helpers, locmem mail, stub `/accounts/crear-cuenta/`
2. US1 → login links (MVP demo)
3. US2 → pending user + confirmation mail + no session
4. US3 → Spanish validation, no mail on errors
5. US4 → confirm link activates and signs in
6. US7 → username-keyed password reset
7. US5 → resend + inactive login copy
8. US6 → back to login from alta
9. Polish → `manage.py test misas` + browser pass + ruff

### Parallel Team Strategy

1. Team completes Setup + Foundational together
2. Then: A = US1 → US2 → US3 → US4 (`login.html` / signup / confirm); B = US7 tests after US1 link exists, implement reset form after A’s `confirmar_correo` exists for token-isolation tests; C = US5/US6 after A’s US4

---

## Notes

- [P] tasks = different files, no dependencies
- No migrations and no custom `User` model; confirmation is `is_active`
- Email is **not** unique; reset and resend key off **username**
- Never email or HTML-display the password
- Generic visitor copy on resend/reset (no username enumeration)
- Do not mutate `Templo` / `Servicio` on pending credentials
- Commit after each task or logical group
- Stop at checkpoints to validate the story independently
