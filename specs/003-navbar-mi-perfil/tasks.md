---
description: "Task list for navegación de sesión y página Mi perfil"
---

# Tasks: Navegación de sesión y página Mi perfil

**Input**: Design documents from `/specs/003-navbar-mi-perfil/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included. Spec independent tests, constitution II (navbar is on temple listing/detail via `base.html`), and `quickstart.md` automated checks. Write tests first and confirm they fail before implementation. Do not weaken existing temple/service coverage in `misas/tests.py`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Existing Django monolith: `site1/` project, `misas/` app (not `src/`).

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Shared test helpers; the Django project and `contrib.auth` login already exist. No new packages or migrations.

- [X] T001 Add a new `TestCase` helper class in `misas/tests.py` (do not change behavior of existing temple/service test classes) that builds a Django `User` (`username` always set) with helpers for filled vs empty `first_name`, `last_name`, and `email`, plus anonymous and `force_login` `Client`s

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Auth redirect settings + named perfil route so `{% url 'misas:perfil' %}` and post-login redirect do not 404. Do **not** wrap the view with `login_required` yet (that is US4) and do **not** fill account fields yet (that is US3).

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 [P] Set `LOGIN_REDIRECT_URL` to `"/misas/perfil/"` and `LOGOUT_REDIRECT_URL` to `"/misas/"` in `site1/settings.py`. Keep `LOGIN_URL` as `"/accounts/login/"`
- [X] T003 [P] Add thin `mi_perfil` in `misas/views.py` that only `render`s `misas/perfil.html` (no extra context; auth context processor already exposes `user`). No `User` model changes. No `login_required` yet
- [X] T004 [P] Add path `perfil/` named `perfil` in `misas/urls.py` (`GET /misas/perfil/`, **no user id in the path**) pointing at `mi_perfil`
- [X] T005 [P] Create stub `misas/templates/misas/perfil.html` extending `misas/templates/base.html` with `{% block title %}Mi perfil{% endblock %}` so the route returns `200` for a logged-in client. No field list and no logout form yet

**Checkpoint**: Foundation ready — `/misas/perfil/` resolves; login/logout redirect settings exist; navbar still unchanged; perfil still public until US4

---

## Phase 3: User Story 1 - Entrar a iniciar sesión desde la barra de navegación (Priority: P1) 🎯 MVP

**Goal**: Every `base.html` screen shows Spanish **Iniciar sesión** (not **Login**) to the existing `/accounts/login/` when the visitor is anonymous, and hides that link once there is a session.

**Independent Test**: Signed-out GET of Inicio: bar shows **Iniciar sesión** → `/accounts/login/`, not **Mi perfil**, not English **Login**. Follow the link to the existing Spanish login. After sign-in, **Iniciar sesión** is gone from the bar.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T006 [US1] Add failing `Client` tests in `misas/tests.py`: anonymous GET `misas:index` (and at least one other `base.html` screen, e.g. `misas:templo`) contains **Iniciar sesión** and `/accounts/login/`; MUST NOT contain a navbar **Login** or `{% url 'misas:login' %}` / a `misas:login` href; MUST NOT contain **Mi perfil**; authenticated GET of the same page MUST NOT contain navbar **Iniciar sesión**

### Implementation for User Story 1

- [X] T007 [US1] In `misas/templates/base.html`, replace the always-on **Login** item (`misas:login`) with `{% if not user.is_authenticated %}` → **Iniciar sesión** linking to `{% url 'login' %}` (`/accounts/login/`). Keep **Inicio** → `misas:index` inside `#navContent`. When authenticated, do not render **Iniciar sesión**. Do not add **Mi perfil** yet (US2)

**Checkpoint**: Anonymous visitors can reach the existing login from the bar; signed-in visitors no longer see that link. **Mi perfil** may still be absent

---

## Phase 4: User Story 2 - Abrir Mi perfil desde la barra cuando hay sesión (Priority: P1)

**Goal**: Authenticated bar shows **Mi perfil** with person icon `bi-person-circle` to `misas:perfil`. Anonymous bar still has no **Mi perfil**.

**Independent Test**: Signed-in GET of Inicio: bar shows **Mi perfil** plus icon, not **Iniciar sesión**. Follow the link to `/misas/perfil/`. Signed-out GET: no **Mi perfil**.

### Tests for User Story 2

- [X] T008 [US2] Add failing tests in `misas/tests.py`: authenticated GET `misas:index` contains **Mi perfil**, `bi-person-circle`, and the perfil URL; MUST NOT contain navbar **Iniciar sesión**; anonymous GET MUST NOT contain **Mi perfil**

### Implementation for User Story 2

- [X] T009 [US2] In `misas/templates/base.html`, when `user.is_authenticated`, render **Mi perfil** with `<i class="bi bi-person-circle">` linking to `{% url 'misas:perfil' %}`. Keep the link inside `#navContent` (collapsed menu). MUST NOT show **Iniciar sesión** and **Mi perfil** at the same time. MUST NOT add a permanent **Cerrar sesión** item to the bar

**Checkpoint**: Session-aware bar is complete (US1+US2). Perfil page may still be an empty stub

---

## Phase 5: User Story 3 - Consultar la información de la cuenta (Priority: P1)

**Goal**: Authenticated GET of Mi perfil shows this user’s `username`, `first_name`, `last_name`, `email`, and `date_joined` in Spanish cream/gold card UI. Empty optional names/email → **No registrado**. Never show password or secrets. Mark **Mi perfil** active in the bar.

**Independent Test**: User with names and email sees those values plus usuario and fecha de alta. User with empty names/email sees **No registrado** for those fields. Password/hash absent. Looks like the directory (card, cream/gold), not an unstyled dump.

### Tests for User Story 3

- [X] T010 [US3] Add failing tests in `misas/tests.py`: authenticated GET `misas:perfil` is `200` and shows labels **Usuario**, **Nombre**, **Apellidos**, **Correo electrónico**, **Fecha de alta**; filled `username` / `first_name` / `last_name` / `email` appear; empty `first_name`, `last_name`, or `email` show **No registrado** (MUST NOT invent a value); `date_joined` is present; response MUST NOT contain `user.password` or the hash; MUST NOT include an edit/save form for those fields; second user’s GET MUST NOT contain the first user’s `username`

### Implementation for User Story 3

- [X] T011 [US3] Fill `misas/templates/misas/perfil.html`: extend `base.html`; cream/gold `card bg-surface border-subtle shadow-sm rounded-3`; Spanish labels. Show `user.username` (**Usuario**, always set), `user.first_name` (**Nombre**; empty → **No registrado**), `user.last_name` (**Apellidos**; empty → **No registrado**), `user.email` (**Correo electrónico**; empty → **No registrado**), `user.date_joined` (**Fecha de alta**, always set, localized via `|date`). MUST NOT output `password`, `is_staff`, `is_superuser`, `last_login`, or groups. No `ModelForm` / edit controls
- [X] T012 [US3] On `misas:perfil`, mark the **Mi perfil** `nav-link` as `active` in `misas/templates/base.html` (same visual language as the existing bar). Do not change **Inicio**’s destination

**Checkpoint**: Own account data is visible and empty fields are explicit. Page may still be reachable while anonymous until US4; logout control may wait for US4

---

## Phase 6: User Story 4 - Proteger Mi perfil y permitir cerrar sesión (Priority: P1)

**Goal**: Anonymous GET perfil redirects to login with `next`; after login, land on perfil. Authenticated GET of login does not show the guest form. **Cerrar sesión** is a CSRF POST to `logout`; then Inicio as visitor.

**Independent Test**: Signed-out `/misas/perfil/` → login, then after sign-in → own perfil. POST logout → Inicio with **Iniciar sesión** in the bar. Two accounts see only their own data (already asserted in US3; keep green). Browser back to perfil asks for login again.

### Tests for User Story 4

- [X] T013 [US4] Add failing tests in `misas/tests.py`: anonymous GET `misas:perfil` is `302` to `/accounts/login/` with `next` pointing at perfil (body MUST NOT include account fields); login POST with that `next` yields perfil `200`; authenticated GET `login` is `302` away from the guest form (MUST NOT re-display **Iniciar sesión** form as if anonymous); authenticated POST `{% url 'logout' %}` (`/accounts/logout/`) with CSRF is `302` to `/misas/`; follow-up GET `misas:index` shows **Iniciar sesión** again; GET `/accounts/logout/` MUST NOT log the user out

### Implementation for User Story 4

- [X] T014 [US4] Wrap `mi_perfil` with `login_required` in `misas/views.py`. CSRF stays enabled. Bind only `request.user` (no user id in the URL). POST to `/misas/perfil/` MUST NOT update `User`
- [X] T015 [P] [US4] In `misas/templates/misas/perfil.html`, add a POST form to `{% url 'logout' %}` with `{% csrf_token %}` and button **Cerrar sesión** (`btn-outline-brand`). No GET logout link. No second logout item in `misas/templates/base.html`
- [X] T016 [P] [US4] In `site1/urls.py`, register `accounts/login/` with `LoginView.as_view(redirect_authenticated_user=True)` **before** `include("django.contrib.auth.urls")` so authenticated GET login redirects (`next` if safe, else `LOGIN_REDIRECT_URL`). Keep using `misas/templates/registration/login.html`

**Checkpoint**: Perfil is private to the signed-in user; logout returns the visitor navbar; US1–US3 still pass

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Full quickstart validation, Spanish UI, CSRF, no scope creep (no profile edit, no temple/service changes)

- [X] T017 Run `python manage.py test misas` from repo root until US1–US4 cases in `specs/003-navbar-mi-perfil/quickstart.md` pass (existing temple/service tests MUST stay green)
- [X] T018 Browser-pass `specs/003-navbar-mi-perfil/quickstart.md` against `misas/templates/base.html` and `misas/templates/misas/perfil.html`: desktop bar, collapsed `#navContent` menu, login, perfil fields / **No registrado**, active nav, authenticated login redirect, POST logout, back-button to perfil asks for login
- [X] T019 Confirm out of scope in `misas/templates/misas/perfil.html` and `misas/templates/base.html`: no profile edit, no password change, no registration, no staff flags, no templo/horario lists, no always-on logout in the navbar; `{% csrf_token %}` remains on the logout form
- [X] T020 Run `pre-commit run ruff-check --all-files` and `pre-commit run ruff-format --all-files` after Python edits; fix reported issues in `misas/views.py`, `misas/urls.py`, `misas/tests.py`, `site1/settings.py`, `site1/urls.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational
  - Sequential for one implementer: US1 → US2 → US3 → US4 (shared `base.html` / `perfil.html` / `views.py`)
  - US4 tests can be drafted after Phase 2, but do **not** add `login_required` until US3 content tests exist
- **Polish (Phase 7)**: Depends on US1–US4 complete

### User Story Dependencies

- **User Story 1 (P1)**: After Phase 2. MVP. Anonymous **Iniciar sesión** → `login`. Hides that link when authenticated. No dependency on US2–US4
- **User Story 2 (P1)**: After Phase 2 named `misas:perfil` route. Adds authenticated **Mi perfil** + icon on `base.html`. Independently testable as nav-only
- **User Story 3 (P1)**: After stub `perfil.html` from Phase 2. Fills fields + active nav. Can be tested with `force_login` before US4
- **User Story 4 (P1)**: After Phase 2 settings. Apply `login_required`, logout form, and `redirect_authenticated_user` after US3 so content tests stay valid

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Navbar anon branch (US1) before authenticated **Mi perfil** branch (US2) — same file `misas/templates/base.html`
- Field markup (US3) before login wall / logout (US4)
- Story complete before next priority if working sequentially

### Parallel Opportunities

- T002, T003, T004, T005 in parallel after T001 (settings / views / urls / stub template — different files)
- T015 and T016 in parallel after T013 (perfil logout form vs `site1/urls.py` LoginView)
- After Phase 2, a second person could draft US4 tests (T013) while US1 proceeds, but do **not** add `login_required` until US3 GET tests exist
- Do **not** parallelize tasks that edit the same file (`misas/tests.py`, `misas/templates/base.html`, `misas/templates/misas/perfil.html`, `misas/views.py`)

---

## Parallel Example: Foundational

```bash
# After T001:
Task: "Set LOGIN_REDIRECT_URL and LOGOUT_REDIRECT_URL in site1/settings.py"
Task: "Add mi_perfil view in misas/views.py"
Task: "Add perfil route in misas/urls.py"
Task: "Create stub misas/templates/misas/perfil.html"
```

## Parallel Example: User Story 4

```bash
# After T013 tests exist and fail, and T014 login_required is in place (or T014 first if views.py vs template/urls):
Task: "Add CSRF POST Cerrar sesión form in misas/templates/misas/perfil.html"
Task: "Register LoginView redirect_authenticated_user in site1/urls.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: anonymous bar shows working **Iniciar sesión**; signed-in bar hides it
5. Continue US2–US4 before calling the feature done (**Mi perfil**, data, login wall, and logout are also P1)

### Incremental Delivery

1. Setup + Foundational → test helpers, redirect settings, stub `/misas/perfil/`
2. US1 → **Iniciar sesión** in the bar (MVP demo)
3. US2 → **Mi perfil** + icon when authenticated
4. US3 → read-only account fields + **No registrado** + active nav
5. US4 → `login_required`, POST logout, authenticated login redirect
6. Polish → `manage.py test misas` + browser pass + ruff

### Parallel Team Strategy

1. Team completes Setup + Foundational together
2. Then: A = US1 then US2 then US3 (`base.html` + `perfil.html`), B = US4 tests then `login_required` / logout / LoginView after A’s US3 GET tests exist

---

## Notes

- [P] tasks = different files, no dependencies
- No migrations and no custom `User` model
- Do not show `password`, staff flags, or another user’s fields
- Do not add profile edit, password change, or navbar logout
- Do not mutate `Templo` / `Servicio`
- Commit after each task or logical group
- Stop at checkpoints to validate the story independently
