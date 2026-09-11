---
description: "Task list for foto y edición de datos del templo"
---

# Tasks: Foto y edición de datos del templo

**Input**: Design documents from `/specs/002-templo-foto-edicion/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included. Spec independent tests plus constitution II (create/edit forms, temple listing/detail). Write tests first and confirm they fail before implementation. Do not weaken existing `ServiciosEditorTestCase` coverage in `misas/tests.py`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Existing Django monolith: `site1/` project, `misas/` app (not `src/`).

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Dependencies and ignore rules this feature needs; the Django project already exists

- [X] T001 [P] Add `Pillow` to `requirements.txt` (required by `ImageField`)
- [X] T002 [P] Add `media/` to `.gitignore` so local uploads under `MEDIA_ROOT` are not committed

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Media config + `Templo.imagen` schema. Do **not** wrap create/edit with `login_required` yet (that is US4) so US1–US3 can still be exercised with `force_login`.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 [P] Set `MEDIA_ROOT` to `BASE_DIR / "media"` and `MEDIA_URL` to `"/media/"` in `site1/settings.py`
- [X] T004 [P] When `DEBUG` is on, serve media via `static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)` in `site1/urls.py`
- [X] T005 Replace unused `Templo.imagen_url` with `Templo.imagen` (`ImageField`, `upload_to="templos/"`, `blank=True`, `null=True` — optional; empty allowed) in `misas/models.py`. Do not keep both fields
- [X] T006 Generate the migration for T005 with `python manage.py makemigrations misas` (do **not** edit generated files by hand). Result lives under `misas/migrations/`
- [X] T007 Add a new `TestCase` helper class in `misas/tests.py` (do not modify `ServiciosEditorTestCase` behavior) that creates a Django `User`, a `Templo` with required `nombre` and `direccion`, a logged-in `Client`, and a tiny in-memory PNG `SimpleUploadedFile` for valid uploads (FR-014: any authenticated user may edit any temple)

**Checkpoint**: Foundation ready — `Templo.imagen` exists; media URLs configured; tests can log in and build a tiny PNG; create/edit views still unprotected until US4

---

## Phase 3: User Story 1 - Subir una foto al crear un templo (Priority: P1) 🎯 MVP

**Goal**: Authenticated editor can create a templo with required `nombre` and `direccion`, optional `alias` (empty string allowed), and optional photo; public ficha/list show the file or the existing placeholder.

**Independent Test**: Log in, open `/misas/templo/nuevo/`, submit name + address + valid photo, land on the public ficha with that image. Repeat without photo: placeholder, not a broken `<img>`. Invalid file or missing name/address: Spanish errors, no row.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T008 [US1] Add failing `Client` tests in `misas/tests.py` for GET `misas:nuevo_templo` (`/misas/templo/nuevo/`) authenticated `200` with `nombre`, `direccion`, `alias`, `imagen`, and `csrfmiddlewaretoken`; POST without `imagen` inserts one `Templo` and the public ficha uses the “sin foto” placeholder (never a broken image); POST with a tiny valid JPEG/PNG persists `imagen` and public ficha/list HTML includes `templo.imagen.url`; POST missing `nombre` or `direccion` (required on create) does not insert; POST non-image (e.g. `.txt`) or file larger than **5 MB** does not insert

### Implementation for User Story 1

- [X] T009 [P] [US1] Expand `TemploForm` in `misas/forms.py`: fields `nombre` (required), `direccion` (required), `alias` (optional; empty string allowed), `imagen` (optional; `FileExtensionValidator` JPEG `jpg`/`jpeg`, PNG, WebP). `clean_imagen` rejects files larger than **5 MB** with a Spanish error. Widget: `FileInput` (no clear checkbox). Spanish labels; `form-control` widgets
- [X] T010 [P] [US1] Restyle `misas/templates/misas/newtemplo.html` to match `misas/templates/misas/edit_servicios.html` (`card bg-surface border-subtle shadow-sm rounded-3`, `{% csrf_token %}`, `method="post"` `enctype="multipart/form-data"`, `btn btn-gold` “Guardar”, Spanish errors inside the card). Include `nombre`, `direccion`, `alias`, `imagen`
- [X] T011 [US1] In `templo_form` in `misas/views.py`, bind `request.POST` and `request.FILES`, persist on valid save, **redirect to `misas:templo`**. Invalid POST re-renders `200` with Spanish errors and MUST NOT insert. Do not accept a client-supplied templo id

**Checkpoint**: Logged-in create with/without photo works; public ficha reflects stored `imagen` or placeholder; edit screen may not exist yet

---

## Phase 4: User Story 2 - Corregir nombre, dirección o alias de un templo existente (Priority: P1)

**Goal**: Dedicated edit screen loads current text fields; editor can change `nombre`, `direccion`, and/or `alias` independently; unmodified fields keep prior values.

**Independent Test**: Open `/misas/templo/<uuid>/editar/`, change only the name, save, confirm the public ficha shows the new name and the same address/alias. Empty name or address: Spanish error, prior data intact. Unknown UUID: `404`.

### Tests for User Story 2

- [X] T012 [US2] Add failing tests in `misas/tests.py`: authenticated GET `misas:editar_templo` (`/misas/templo/<uuid:id_templo>/editar/`) `200` with current `nombre`, `direccion`, `alias` filled; POST changing only `nombre` updates `nombre` and leaves `direccion` and `alias` unchanged; POST with empty `nombre` or `direccion` (required on edit) is `200` with Spanish errors and MUST NOT overwrite; unknown UUID → `404`

### Implementation for User Story 2

- [X] T013 [P] [US2] Add route `templo/<uuid:id_templo>/editar/` named `editar_templo` in `misas/urls.py` (templo id from the URL, not the body)
- [X] T014 [P] [US2] Create `misas/templates/misas/edit_templo.html` with the same cream/gold card language as `misas/templates/misas/edit_servicios.html`, fields `nombre` (required), `direccion` (required), `alias` (optional; empty string allowed), `{% csrf_token %}`, `enctype="multipart/form-data"`, `btn btn-gold` “Guardar”, Spanish errors inside the card
- [X] T015 [US2] Add `templo_edit` in `misas/views.py`: `get_object_or_404(Templo, pk=...)`; GET shows `TemploForm` bound to the instance; valid POST updates that templo and **redirects to `misas:templo`**; invalid POST re-renders `200` without saving. A field not submitted as changed MUST keep its previous value
- [X] T016 [P] [US2] Add an “Editar templo” (or equivalent Spanish) link to `{% url 'misas:editar_templo' templo.id %}` on the public ficha in `misas/templates/misas/templo.html`, next to the existing “Agregar Servicio” link. Do not remove service editing

**Checkpoint**: Text edit works and public ficha updates; photo replace on this screen may wait for US3

---

## Phase 5: User Story 3 - Agregar o cambiar la foto de un templo existente (Priority: P1)

**Goal**: Same edit screen can add a photo if none, replace the current one, or leave it unchanged when no new file is chosen. Invalid files do not touch prior photo or text.

**Independent Test**: Temple without photo: attach a valid image, save, ficha shows it. Temple with photo: attach another, ficha shows the new one. Save text without a file: photo unchanged. `.txt` upload: Spanish error, previous photo kept.

### Tests for User Story 3

- [X] T017 [US3] Add failing tests in `misas/tests.py`: templo without `imagen` + valid PNG POST sets `imagen`; templo with `imagen` + new valid file replaces it (public HTML uses the new `templo.imagen.url`); POST without a new file keeps `imagen` unchanged (empty upload MUST NOT clear); non-image or file larger than **5 MB** does not persist and MUST NOT change existing `imagen` or text fields

### Implementation for User Story 3

- [X] T018 [US3] In `templo_edit` in `misas/views.py`, bind `request.FILES` as well as `request.POST`. Empty `imagen` upload MUST NOT clear an existing file (add / keep / replace only; no delete-without-replace). Valid new file becomes the single current photo (`upload_to="templos/"`)
- [X] T019 [US3] In `misas/templates/misas/edit_templo.html`, show a preview of the current `imagen` when present, then the file input. Do not render a “clear” checkbox. Keep placeholder behavior on public `misas/templates/misas/index.html` and `misas/templates/misas/templo_header.html` (`{% if templo.imagen %}` / church icon) — they MUST display the stored file or the placeholder, never a broken image

**Checkpoint**: Create (US1) and text edit (US2) still work; photo add/replace on edit matches data-model.md

---

## Phase 6: User Story 4 - Solo quienes iniciaron sesión pueden crear o editar un templo (Priority: P1)

**Goal**: Anonymous visitors never see or POST create/edit; after login they return via `next`. Public listing and ficha stay public.

**Independent Test**: Signed-out GET/POST of `/misas/templo/nuevo/` and `/misas/templo/<id>/editar/` redirect to login and persist nothing. After sign-in, the requested screen loads. Index and temple detail remain `200` without a session.

### Tests for User Story 4

- [X] T020 [US4] Add failing tests in `misas/tests.py`: anonymous GET/POST `misas:nuevo_templo` and `misas:editar_templo` are `302` to `/accounts/login/` with `next` set (body MUST NOT include the form); anonymous POST MUST NOT insert or update a `Templo`; login then `next` yields `200`; `misas:index` and `misas:templo` remain `200` without auth and still show `imagen` or placeholder

### Implementation for User Story 4

- [X] T021 [US4] Wrap `templo_form` and `templo_edit` with `login_required` in `misas/views.py` (CSRF stays enabled; FR-014: no parish-ownership check this iteration)
- [X] T022 [US4] Keep `misas:index` and `misas:templo` public in `misas/views.py`. Leave the “Editar templo” link on `misas/templates/misas/templo.html` so anonymous visitors hit the login contract via `next`

**Checkpoint**: Only authenticated users mutate ficha data; public directory still works unsigned

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Verify the whole feature against quickstart and constitution (Spanish UI, CSRF, no templo delete, no service edits)

- [X] T023 Run `python manage.py test misas` from repo root until US1–US4 cases in `specs/002-templo-foto-edicion/quickstart.md` pass (existing service-editor tests MUST stay green)
- [X] T024 Browser-pass `specs/002-templo-foto-edicion/quickstart.md` against `misas/templates/misas/newtemplo.html`, `misas/templates/misas/edit_templo.html`, public `misas/templates/misas/index.html` / `misas/templates/misas/templo.html`: create with photo, text-only edit, photo replace, login wall, placeholder vs real image
- [X] T025 Confirm `{% csrf_token %}` remains on create and edit forms in `misas/templates/misas/newtemplo.html` and `misas/templates/misas/edit_templo.html`; no templo-delete control; no create/update/delete of `Servicio` on these screens; no clear-photo-without-replace control
- [X] T026 Run `pre-commit run ruff-check --all-files` and `pre-commit run ruff-format --all-files` after Python edits; fix reported issues in `misas/models.py`, `misas/forms.py`, `misas/views.py`, `misas/urls.py`, `misas/tests.py`, `site1/settings.py`, `site1/urls.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational
  - Sequential for one implementer: US1 → US2 → US3 → US4 (shared `TemploForm` / `views.py` / edit template)
  - US4 can be prepared (tests) in parallel after Phase 2, but wrapping views last avoids breaking US1–US3 `force_login` tests mid-work
- **Polish (Phase 7)**: Depends on US1–US4 complete

### User Story Dependencies

- **User Story 1 (P1)**: After Phase 2. MVP. Create + optional photo. No dependency on US2–US4
- **User Story 2 (P1)**: After Phase 2. Needs `TemploForm` text fields from US1; new route/template/view. Independently testable as text-only edit
- **User Story 3 (P1)**: After US2 edit view/template exist. Adds `request.FILES` keep/replace behavior and preview
- **User Story 4 (P1)**: After Phase 2 (`LOGIN_URL` + login template already from 001). Apply after US1–US3 so authenticated tests stay valid with `login_required`

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Form widgets before (or parallel with) create template
- Route + template before (or parallel with) edit view
- Bind `FILES` before claiming photo-replace story done
- Story complete before next priority if working sequentially

### Parallel Opportunities

- T001 and T002 in parallel (different files)
- T003 and T004 in parallel (different files)
- T009 and T010 in parallel after T008
- T013, T014, T016 in parallel after T012 (urls / edit template / public ficha link)
- After Phase 2, a second person could draft US4 tests (T020) while US1 proceeds, but do **not** add `login_required` until US1–US3 POST tests exist
- Do **not** parallelize tasks that edit the same file (`misas/tests.py`, `misas/forms.py`, `misas/views.py`, `misas/templates/misas/edit_templo.html`)

---

## Parallel Example: User Story 1

```bash
# After T008 tests exist and fail:
Task: "Expand TemploForm (nombre, direccion, alias, imagen validators) in misas/forms.py"
Task: "Restyle newtemplo.html multipart create card"
```

## Parallel Example: User Story 2

```bash
# After T012 tests exist and fail:
Task: "Add editar_templo route in misas/urls.py"
Task: "Create edit_templo.html cream/gold form"
Task: "Add Editar templo link in templo.html"
```

## Parallel Example: Foundational

```bash
Task: "Set MEDIA_ROOT and MEDIA_URL in site1/settings.py"
Task: "Serve media in DEBUG in site1/urls.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: authenticated create with optional photo + public ficha/list display
5. Continue US2–US4 before calling the feature done (edit screen and login wall are also P1)

### Incremental Delivery

1. Setup + Foundational → Pillow, media, `Templo.imagen`
2. US1 → create with photo (MVP demo)
3. US2 → edit nombre / dirección / alias
4. US3 → add or replace photo on edit
5. US4 → anonymous cannot mutate
6. Polish → `manage.py test misas` + browser pass + ruff

### Parallel Team Strategy

1. Team completes Setup + Foundational together
2. Then: A = US1 then US2/US3 (form + templates + views), B = US4 tests then `login_required` after A’s POST tests exist

---

## Notes

- [P] tasks = different files, no dependencies
- One generated migration only; never hand-edit `misas/migrations/`
- Parish-level authorization is out of scope (FR-014)
- Do not delete templos or mutate servicios on these screens
- Do not add “clear photo without replacement”
- Commit after each task or logical group
- Stop at checkpoints to validate the story independently
