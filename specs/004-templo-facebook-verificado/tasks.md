---
description: "Task list for enlace de Facebook y verificación del templo"
---

# Tasks: Enlace de Facebook y verificación del templo

**Input**: Design documents from `/specs/004-templo-facebook-verificado/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included. Spec independent tests, constitution II (temple detail, create/edit forms, service schedules), and `quickstart.md`. Write tests first and confirm they fail before implementation. Do not weaken existing `ServiciosEditorTestCase`, ficha/photo, or navbar coverage in `misas/tests.py`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Existing Django monolith: `site1/` project, `misas/` app (not `src/`).

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Shared test helpers; the Django project, `TemploForm`, create/edit screens, and `templo_header.html` already exist. No new packages.

- [X] T001 Add a new `TestCase` helper class in `misas/tests.py` (do not change behavior of existing temple/service/navbar classes) that reuses a logged-in editor `User`, a staff `User` (`is_staff=True`), a `Templo` with required `nombre` and `direccion`, and helpers for ficha / edit / servicios URLs. Include a sample Facebook URL string for posts

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Schema for `facebook` and `verificado` plus a revoke helper. Do **not** put `verificado` on `TemploForm` yet (never on the form). Do **not** change header UI yet.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Add `Templo.facebook` as `URLField` (optional; `blank=True`, `default=""`, `max_length=500`) and `Templo.verificado` as `BooleanField` (`default=False`) on `Templo` in `misas/models.py`. Add `revocar_verificacion()` that sets `verificado=False` and saves only when it was `True`. Do not add tables. Do not put `verificado` on any form
- [X] T003 Generate the migration for T002 with `python manage.py makemigrations misas` (do **not** edit generated files by hand). Result lives under `misas/migrations/`. Existing rows MUST backfill `verificado=False` and empty `facebook`
- [X] T004 [P] Add `facebook` and `verificado` to `list_display` on `TemploAdmin` in `misas/admin.py`. Do not add a custom admin-only verify workflow (verify UX is the header POST in US3)

**Checkpoint**: Foundation ready — fields exist; create still ignores them in the UI; header unchanged; existing tests should still pass after migration

---

## Phase 3: User Story 1 - Registrar o corregir el enlace de Facebook del templo (Priority: P1) 🎯 MVP

**Goal**: Authenticated editor can set, change, or clear optional `facebook` on the existing alta and edición screens. Invalid URLs do not persist. Create always stores `verificado=False`.

**Independent Test**: Log in, create a templo with `https://www.facebook.com/parroquia`, land on the ficha with that value stored. Create without Facebook: `facebook=""`. Edit to a new URL or to empty without changing nombre/dirección/foto. Invalid text: Spanish error, no insert/update.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T005 [US1] Add failing `Client` tests in `misas/tests.py` for GET `misas:nuevo_templo` and GET `misas:editar_templo` authenticated `200` with `name="facebook"` and CSRF, MUST NOT include a verify checkbox; POST create with `https://www.facebook.com/parroquia` inserts `facebook` and `verificado=False`; POST create without `facebook` inserts `facebook=""`; POST create with `facebook.com/parroquia` (no scheme) stores `https://facebook.com/parroquia`; POST create extra `verificado=1` still yields `verificado=False`; POST create/edit with `facebook=no es una url` is `200` with Spanish error and MUST NOT insert/update; POST edit changing only `facebook` updates `facebook` and leaves `nombre`, `direccion`, `alias`, `imagen` unchanged; POST edit with empty `facebook` stores `""`

### Implementation for User Story 1

- [X] T006 [P] [US1] Add `facebook` to `TemploForm` in `misas/forms.py` (optional; empty string allowed; `max_length=500`). Spanish label (e.g. **Facebook**). `URLInput` with `form-control`. Spanish URL error messages. `clean_facebook`: strip whitespace; if non-empty and no `http://` or `https://` scheme, prefix `https://`. MUST NOT include `verificado` in `Meta.fields`
- [X] T007 [P] [US1] Add the `facebook` field to the create card in `misas/templates/misas/newtemplo.html` (same `form-label` / `form-control` / Spanish error pattern as `nombre`). Keep `{% csrf_token %}` and `btn btn-gold`. Do not add a verificación control
- [X] T008 [P] [US1] Add the `facebook` field to the edit card in `misas/templates/misas/edit_templo.html` the same way. Pre-filled from the instance. Do not add a verificación control
- [X] T009 [US1] Confirm `templo_form` and `templo_edit` in `misas/views.py` persist `facebook` via `TemploForm.save()` (create `302` to `misas:templo`; edit `302` to `misas:templo`; invalid `200` without saving). Extra POST `verificado` MUST be ignored. Empty `facebook` allowed

**Checkpoint**: Logged-in create/edit of Facebook works; public header may still not show the link (US2)

---

## Phase 4: User Story 2 - Abrir el Facebook del templo desde su información (Priority: P1)

**Goal**: Shared `templo_header.html` shows `bi-facebook` plus the stored address as a followable link when `facebook` is set; shows neither when empty. Same block on public ficha and servicios editor.

**Independent Test**: Anonymous GET ficha of a templo with Facebook shows icon + address + `href` with `target="_blank"` `rel="noopener noreferrer"`. Servicios GET (logged in) shows the same. Empty `facebook`: no icon, no href. Listing (`misas:index`) stays unchanged.

### Tests for User Story 2

- [X] T010 [US2] Add failing tests in `misas/tests.py`: anonymous GET `misas:templo` with `facebook` set contains `bi-facebook`, the URL text, `target="_blank"`, and `rel="noopener noreferrer"`; GET `misas:templo_servicios` (authenticated) contains the same; templo with `facebook=""` on both screens MUST NOT contain `bi-facebook` or an empty Facebook `href`; GET `misas:index` is NOT required to show Facebook (listing out of scope)

### Implementation for User Story 2

- [X] T011 [US2] In `misas/templates/misas/templo_header.html`, when `templo.facebook` is non-empty, render `bi-facebook` and the stored address as link text, `href` = `templo.facebook`, `target="_blank"`, `rel="noopener noreferrer"`. When empty, render neither icon nor address. Do not change `misas/templates/misas/index.html`. Keep existing photo/address/Cómo llegar markup

**Checkpoint**: Visitors can follow Facebook from ficha and servicios header; verify UI may still be absent

---

## Phase 5: User Story 3 - El administrador marca un templo como verificado (Priority: P1)

**Goal**: Staff (`is_staff`) can POST mark/unmark from the shared header on ficha and servicios. Create and existing rows start unverified. Header shows **Verificado** when true.

**Independent Test**: Staff POST `verificado=1` then GET ficha/servicios show **Verificado**. POST `verificado=0` removes it. New templo is `verificado=False`. Unknown UUID: `404`. GET verify: `405`.

### Tests for User Story 3

- [X] T012 [US3] Add failing tests in `misas/tests.py`: staff POST `misas:verificar_templo` (`/misas/templo/<uuid>/verificar/`) with CSRF and `verificado=1` sets `True` and `302`s to ficha (or `next` if it is this templo’s ficha or servicios path); staff POST `verificado=0` sets `False`; GET verify is `405`; unknown UUID POST is `404`; create still `verificado=False`; after `verificado=True`, GET ficha and servicios contain **Verificado**; verify-only POST MUST NOT change `nombre`, `direccion`, `alias`, `imagen`, `facebook`, or `Servicio` rows

### Implementation for User Story 3

- [X] T013 [P] [US3] Add route `templo/<uuid:id_templo>/verificar/` named `verificar_templo` in `misas/urls.py` (templo id from the URL, not the body)
- [X] T014 [US3] Add `templo_verificar` in `misas/views.py`: POST only (`405` on GET); `@login_required`; if not `request.user.is_staff` wait until US4 for `403` or implement `403` now; `get_object_or_404`; persist `verificado` from POST `"1"` / `"0"`; CSRF stays on; `next` MUST be a relative path to this templo’s `misas:templo` or `misas:templo_servicios` else redirect to ficha. MUST NOT mutate ficha text/photo/facebook or servicios
- [X] T015 [US3] In `misas/templates/misas/templo_header.html`, when `templo.verificado`, show a clear **Verificado** mark (Spanish). Add a staff-only POST form (`{% if user.is_staff %}`) to `misas:verificar_templo` with `{% csrf_token %}`, hidden `next` = `request.path`, button **Marcar como verificado** (`verificado=1`) or **Quitar verificación** (`verificado=0`) using existing `btn btn-sm` language. Same form on ficha and servicios via this include

**Checkpoint**: Staff can mark/unmark from both screens; non-staff restrictions are US4; revoke-on-edit is US5; asterisk/notes are US6

---

## Phase 6: User Story 4 - Solo el administrador puede verificar (Priority: P1)

**Goal**: Non-staff editors and anonymous visitors cannot change `verificado`. They still see **Verificado** on the public ficha when it is true. Alta/edición forms have no verify control.

**Independent Test**: Editor POST verify → `403`, flag unchanged. Anonymous POST → login `302` with `next`, flag unchanged. Editor GET ficha/servicios has no Marcar/Quitar. Anonymous GET verified ficha shows **Verificado** and no form.

### Tests for User Story 4

- [X] T016 [US4] Add failing tests in `misas/tests.py`: non-staff authenticated POST `misas:verificar_templo` is `403` and MUST NOT change `verificado`; anonymous POST is `302` to `/accounts/login/` with `next` and MUST NOT change `verificado`; non-staff GET ficha and servicios MUST NOT contain **Marcar como verificado** or **Quitar verificación**; anonymous GET of a verified templo contains **Verificado** and MUST NOT contain those buttons; GET create/edit MUST NOT contain a `verificado` checkbox

### Implementation for User Story 4

- [X] T017 [US4] In `misas/views.py`, non-staff POST `templo_verificar` MUST return `403` (do not use admin-site login). Keep `@login_required` for anonymous → `/accounts/login/`. In `misas/templates/misas/templo_header.html`, wrap the verify form so only `user.is_staff` sees it. Confirm `misas/templates/misas/newtemplo.html` and `misas/templates/misas/edit_templo.html` still have no verificación control

**Checkpoint**: Only staff mutate the flag via the header; community can still read **Verificado**

---

## Phase 7: User Story 5 - Editar ficha o servicios revoca la verificación (Priority: P1)

**Goal**: A valid templo edit save or valid servicio create sets `verificado=False` if it was `True` (including when the actor is staff). Invalid saves do not touch the flag.

**Independent Test**: Verified templo + valid edit (nombre or facebook) → `verificado=False`. Verified templo + valid servicio POST → `verificado=False` on that `200`. Invalid facebook/servicio POST leaves `True`. Staff who edit must re-mark.

### Tests for User Story 5

- [X] T018 [US5] Add failing tests in `misas/tests.py`: templo with `verificado=True` + valid POST `misas:editar_templo` (change `nombre` or `facebook`) persists `verificado=False`; staff valid edit also revokes; valid POST `misas:templo_servicios` insert revokes and the `200` response is unverified; invalid templo POST (`facebook=no es una url` or empty `nombre`) and invalid servicio POST do not persist and MUST NOT change `verificado`; templo already `False` stays `False` after a valid save

### Implementation for User Story 5

- [X] T019 [US5] In `templo_edit` in `misas/views.py`, after a valid `TemploForm`, set `verificado=False` when it was `True` (use `commit=False` + `revocar_verificacion` or equivalent so photo/text/facebook/flag are one write). Invalid POST MUST NOT call revoke. Create path stays default `False`
- [X] T020 [US5] In `templo_servicios_edit` in `misas/views.py`, after a valid `Servicio` insert, call `templo.revocar_verificacion()` and re-bind `templo` in context so `misas/templates/misas/templo_header.html` on the same `200` shows unverified. Invalid POST MUST NOT revoke. Do **not** add service modify/delete UI

**Checkpoint**: US1–US4 still work; verified temples drop the mark after a real ficha or servicio save

---

## Phase 8: User Story 6 - Avisos de validación pendiente y de fechas especiales (Priority: P1)

**Goal**: Unverified temples show a small `*` after the name and «La información de este templo aún está sujeta a validación.» at the foot of the header. All temples show «La información y horarios pueden estar sujetos a modificaciones o excepciones en fechas especiales/festividades.» Verified temples have no asterisk and no pending note.

**Independent Test**: Anonymous ficha unverified: `*` after name + both notes. Verified: **Verificado**, festivities note, no `*` / no pending note. Same on servicios. After US5 revoke, pending UI is visible immediately.

### Tests for User Story 6

- [X] T021 [US6] Add failing tests in `misas/tests.py`: GET ficha and servicios for `verificado=False` contain `*` immediately after `templo.nombre` and exact text «La información de este templo aún está sujeta a validación.»; GET for `verificado=True` contains **Verificado**, MUST NOT contain that pending sentence, and MUST NOT put `*` after the name; both states contain exact «La información y horarios pueden estar sujetos a modificaciones o excepciones en fechas especiales/festividades.»; after a US5 revoke, the next GET (or the servicios `200`) shows asterisk + pending note

### Implementation for User Story 6

- [X] T022 [US6] In `misas/templates/misas/templo_header.html`, if not `templo.verificado`, render a small `*` immediately after the name and, at the foot of that card, «La información de este templo aún está sujeta a validación.» If `verificado`, omit both. Always render at the foot: «La información y horarios pueden estar sujetos a modificaciones o excepciones en fechas especiales/festividades.» Keep cream/gold header language; do not add these notes to `misas/templates/misas/index.html`

**Checkpoint**: All six stories independently observable on ficha and servicios header

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Full-suite tests, browser pass, security/UI constraints, lint

- [X] T023 Run `python manage.py test misas` from repo root until US1–US6 cases in `specs/004-templo-facebook-verificado/quickstart.md` pass (existing service-editor, ficha/photo, and navbar tests MUST stay green)
- [X] T024 Browser-pass `specs/004-templo-facebook-verificado/quickstart.md` against `misas/templates/misas/newtemplo.html`, `misas/templates/misas/edit_templo.html`, `misas/templates/misas/templo_header.html` on ficha and servicios: Facebook create/click-out, staff mark/unmark, editor revoke, servicio create revoke, asterisk/notes, no verify button when signed out
- [X] T025 Confirm `{% csrf_token %}` on create, edit, and verify forms in `misas/templates/misas/newtemplo.html`, `misas/templates/misas/edit_templo.html`, and `misas/templates/misas/templo_header.html`; no templo-delete control; no new service modify/delete UI; listing `misas/templates/misas/index.html` unchanged for Facebook/asterisk/notes
- [X] T026 Run `pre-commit run ruff-check --all-files` and `pre-commit run ruff-format --all-files` after Python edits; fix reported issues in `misas/models.py`, `misas/forms.py`, `misas/views.py`, `misas/urls.py`, `misas/admin.py`, `misas/tests.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational
  - Sequential for one implementer: US1 → US2 → US3 → US4 → US5 → US6 (shared `templo_header.html` / `views.py` / `tests.py`)
- **Polish (Phase 9)**: Depends on US1–US6 complete

### User Story Dependencies

- **User Story 1 (P1)**: After Phase 2. MVP. Facebook on create/edit. No dependency on US2–US6
- **User Story 2 (P1)**: After Phase 2. Needs stored `facebook` from US1 to be visible; independently testable by setting `Templo.facebook` in tests
- **User Story 3 (P1)**: After Phase 2. Verify POST + header mark. Can be tested by setting `verificado` in the DB if header exists
- **User Story 4 (P1)**: After US3 route/view exist. Tightens 403 / hide form
- **User Story 5 (P1)**: After US1 save paths and US3 flag exist. Hooks `templo_edit` and `templo_servicios_edit`
- **User Story 6 (P1)**: After header exists (US2/US3). Adds asterisk + notes on the same include

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Model/migration (Phase 2) before forms
- Form before (or parallel with) create/edit templates
- Route before verify view
- View before claiming staff verify done
- Story complete before next priority if working sequentially

### Parallel Opportunities

- T003 and T004 in parallel after T002 (migration vs `admin.py`)
- T006, T007, T008 in parallel after T005 (form vs two templates)
- T013 in parallel with drafting T014 after T012 (urls vs view — do not both edit `urls.py`)
- After Phase 2, a second person could draft US2 header tests (T010) while US1 proceeds
- Do **not** parallelize tasks that edit the same file (`misas/tests.py`, `misas/views.py`, `misas/forms.py`, `misas/templates/misas/templo_header.html`)

---

## Parallel Example: User Story 1

```bash
# After T005 tests exist and fail:
Task: "Add facebook to TemploForm in misas/forms.py"
Task: "Add facebook field in newtemplo.html"
Task: "Add facebook field in edit_templo.html"
```

## Parallel Example: Foundational

```bash
# After T002 model fields exist:
Task: "Generate migration with makemigrations misas"
Task: "Add facebook and verificado to TemploAdmin list_display in misas/admin.py"
```

## Parallel Example: User Story 3

```bash
# After T012 tests exist and fail:
Task: "Add verificar_templo route in misas/urls.py"
# Then view in misas/views.py (same story, not parallel with urls if one person)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: authenticated create/edit of optional Facebook
5. Continue US2–US6 before calling the feature done (display, staff verify, revoke, notes are also P1)

### Incremental Delivery

1. Setup + Foundational → `facebook` / `verificado` schema
2. US1 → create/edit Facebook (MVP demo)
3. US2 → icon + address on shared header
4. US3 → staff mark/unmark
5. US4 → 403 / hide control
6. US5 → revoke on ficha save and servicio create
7. US6 → asterisk + Spanish notes
8. Polish → `manage.py test misas` + browser pass + ruff

### Parallel Team Strategy

1. Team completes Setup + Foundational together
2. Then: A = US1 then US2 (form + header Facebook), B = US3/US4 (verify route) after agreeing header ownership, then US5/US6 on `views.py` / header

---

## Notes

- [P] tasks = different files, no dependencies
- One generated migration only; never hand-edit `misas/migrations/`
- Parish-level authorization for ficha/service edits is out of scope; verification is `is_staff` only
- Do not add service modify/delete screens; only hook existing create
- Do not put Facebook/asterisk/notes on listing cards
- Commit after each task or logical group
- Stop at checkpoints to validate the story independently
