---
description: "Task list for editor de servicios del templo"
---

# Tasks: Editor de servicios del templo

**Input**: Design documents from `/specs/001-servicios-editor-ui/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included. Spec requires critical-path schedule tests; constitution II requires tests for create/edit forms and service schedules. Write tests first and confirm they fail before implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Existing Django monolith: `site1/` project, `misas/` app (not `src/`).

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Directories this feature needs; the Django project already exists

- [X] T001 Create `misas/templates/registration/` so Django `contrib.auth` can load a themed login template

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Login route + shared test helpers. Do **not** wrap the editor view yet (that is US3) so US1/US2 can still be exercised; `LOGIN_URL` must exist before US3 redirects.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 [P] Set `LOGIN_URL` to `/accounts/login/` in `site1/settings.py`
- [X] T003 [P] Include `django.contrib.auth.urls` at `accounts/` in `site1/urls.py`
- [X] T004 [P] Create Spanish login form extending `misas/templates/base.html` in `misas/templates/registration/login.html` using listing visual language (`card bg-surface border-subtle shadow-sm rounded-3`, `form-control`, `btn btn-gold`)
- [X] T005 Add shared `TestCase` helpers in `misas/tests.py` that create a Django `User`, a `Templo` (`nombre`, `direccion`), and a logged-in `Client` (FR-010: any authenticated user may open any temple)

**Checkpoint**: Foundation ready — `/accounts/login/` renders; tests can log in; editor view is still unprotected until US3

---

## Phase 3: User Story 1 - Crear un servicio con el formulario existente (Priority: P1) 🎯 MVP

**Goal**: Authenticated editor sees a cream/gold create form in the **upper** card and can persist a valid service (or see Spanish errors without a new row).

**Independent Test**: Log in, open `/misas/templo/<uuid>/servicios/`, submit tipo/día/horas válidas, confirm a `Servicio` is stored for that templo; invalid payload shows errors and does not insert.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T006 [US1] Add failing `Client` tests in `misas/tests.py` for GET `/misas/templo/<uuid:id_templo>/servicios/` (`misas:templo_servicios`) authenticated `200` with create fields; POST `tipo_servicio`, `dia_de_semana`, `hora_inicio` (required `TimeField`) and optional `hora_fin` (`null`/`blank` allowed) persists one `Servicio` with `templo` from the URL not the body; POST with `hora_fin` set and `hora_fin < hora_inicio` does not persist; unknown UUID returns `404`

### Implementation for User Story 1

- [X] T007 [P] [US1] Apply Bootstrap widgets (`form-select` / `form-control`) and Spanish labels on `ServicioForm` fields `tipo_servicio`, `dia_de_semana`, `hora_inicio`, `hora_fin` in `misas/forms.py` (`hora_fin` remains optional)
- [X] T008 [P] [US1] Restyle the **upper** create card in `misas/templates/misas/edit_servicios.html` to match `misas/templates/misas/index.html` (`card bg-surface border-subtle shadow-sm rounded-3`, `{% csrf_token %}`, `btn btn-gold` “Guardar”, Spanish errors inside the card). Keep `{% include "misas/templo_header.html" %}`. Do not add delete/edit controls
- [X] T009 [US1] In `ServicioForm.clean()` in `misas/forms.py` reject when `hora_fin` is set and `hora_fin < hora_inicio` (Spanish error). In `misas/views.py` assign `templo` from the URL after a valid form and do not accept `templo` from POST

**Checkpoint**: Logged-in create path works with styled upper form; list card may still be unstyled until US2

---

## Phase 4: User Story 2 - Ver los servicios ya creados debajo del formulario (Priority: P1)

**Goal**: Lower card shows real `get_servicios()` data grouped by type, or a Spanish empty state.

**Independent Test**: Temple with several services: open editor and read type, day, and hour below the form. Temple with none: Spanish empty copy, not a blank block.

### Tests for User Story 2

- [X] T010 [US2] Add failing tests in `misas/tests.py`: GET lower list shows rows from `Templo.get_servicios()` (`{tipo_display: {dia_display: [hora_inicio, ...]}}`) without fabricating entries; templo with no servicios shows Spanish empty copy

### Implementation for User Story 2

- [X] T011 [US2] Render the **lower** card in `misas/templates/misas/edit_servicios.html` from `templo.get_servicios()`, grouped by type with day and hours, using listing visual language (`card`, cream/gold, readable grouping). Do not invent or drop schedule data
- [X] T012 [US2] Add Spanish empty state in the lower card of `misas/templates/misas/edit_servicios.html` when there are no servicios (not a blank region)

**Checkpoint**: Form (US1) stays on top; existing services (or empty copy) are below

---

## Phase 5: User Story 3 - Solo quienes iniciaron sesión pueden abrir esta pantalla (Priority: P1)

**Goal**: Anonymous visitors never see or POST the editor; after login they return via `next`. Public listing and temple detail stay public.

**Independent Test**: Signed-out GET/POST of the editor redirects to login and inserts nothing. After sign-in, the same temple editor loads. Index and temple detail remain `200` without a session.

### Tests for User Story 3

- [X] T013 [US3] Add failing tests in `misas/tests.py`: anonymous GET `/misas/templo/<uuid>/servicios/` is `302` to login with `next` set (body MUST NOT include the create form or editor list); anonymous POST is `302` and MUST NOT insert a `Servicio`; login then `next` yields editor `200`; `misas:index` and `misas:templo` remain `200` without auth

### Implementation for User Story 3

- [X] T014 [US3] Wrap `templo_servicios_edit` with `login_required` in `misas/views.py` (CSRF stays enabled; FR-010: no parish-ownership check this iteration)
- [X] T015 [US3] Keep the public “Agregar servicio” link to `{% url 'misas:templo_servicios' templo.id %}` in `misas/templates/misas/templo.html` without putting `login_required` on `misas:index` or `misas:templo`

**Checkpoint**: Only authenticated users reach the editor; public schedules still work unsigned

---

## Phase 6: User Story 4 - Rechazar horarios duplicados o superpuestos del mismo tipo (Priority: P1)

**Goal**: Same-type duplicate start or interior overlap vs a sibling with `hora_fin` shows a Spanish form message and does not insert. Adjacent half-open slots are allowed.

**Independent Test**: Existing service: duplicate same type/day/`hora_inicio` fails; 10:00–11:00 then 10:30 fails; 10:00–11:00 then 11:00–12:00 both persist; other type same slot persists.

### Tests for User Story 4

- [X] T016 [US4] Add failing tests in `misas/tests.py` covering: duplicate same `tipo_servicio`, `dia_de_semana`, and `hora_inicio` does not persist; interior overlap vs sibling with `hora_fin` (`nuevo.hora_inicio < existente.hora_fin` **and** `existente.hora_inicio < nuevo.hora_fin`) does not persist; candidate without `hora_fin` treated as a point (`existente.hora_inicio <= nuevo.hora_inicio < existente.hora_fin`); adjacent `10:00–11:00` then `11:00–12:00` same type both persist; different `tipo_servicio` same slot persists; different weekday same type/time persists; existing without `hora_fin` only the duplicate `hora_inicio` rule applies; rejected POST leaves the lower list unchanged

### Implementation for User Story 4

- [X] T017 [US4] In `ServicioForm.clean()` in `misas/forms.py`, compare the candidate to **other** servicios of the **same templo** and reject duplicates: if another servicio has the same `tipo_servicio`, `dia_de_semana`, and `hora_inicio`, the form is invalid. Do not persist. Spanish message on the form
- [X] T018 [US4] In `ServicioForm.clean()` in `misas/forms.py`, overlap **only against siblings that have `hora_fin`**. Intervals are half-open `[hora_inicio, hora_fin)`. If the candidate has `hora_fin`: overlap when `nuevo.hora_inicio < existente.hora_fin` **and** `existente.hora_inicio < nuevo.hora_fin`. If the candidate has no `hora_fin`: treat it as a point at `hora_inicio`; overlap when `existente.hora_inicio <= nuevo.hora_inicio < existente.hora_fin`. Adjacent `10:00–11:00` and `11:00–12:00` are **not** overlap. Spanish message; MUST NOT create the row

**Checkpoint**: Conflict rules match data-model.md; US1 create still works for non-conflicting rows

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Verify the whole editor against quickstart and constitution (Spanish UI, CSRF, no delete scope creep)

- [X] T019 Run `python manage.py test misas` from repo root until the US1–US4 cases in `specs/001-servicios-editor-ui/quickstart.md` pass
- [X] T020 Browser-pass `specs/001-servicios-editor-ui/quickstart.md` against `misas/templates/misas/edit_servicios.html` and `/accounts/login/`: form upper, list/empty lower, login wall, public temple still readable unsigned
- [X] T021 Confirm `{% csrf_token %}` remains on the create form in `misas/templates/misas/edit_servicios.html` and that no delete/edit-existing-service controls were added

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational
  - Sequential for one implementer: US1 → US2 → US3 → US4 (US2 and US4 both touch the create/list page; US4 only needs `forms.py` after US1)
  - US2 can start after T008 (template exists) if staffed separately from US4
- **Polish (Phase 7)**: Depends on US1–US4 complete

### User Story Dependencies

- **User Story 1 (P1)**: After Phase 2. MVP. No dependency on US2–US4
- **User Story 2 (P1)**: After Phase 2. Shares `edit_servicios.html` with US1 (do US1 template restyle first if one person)
- **User Story 3 (P1)**: After Phase 2 (`LOGIN_URL` + login template). Independent of list/overlap, but US1 tests that POST as a logged-in client still apply after `login_required`
- **User Story 4 (P1)**: After Phase 2. Needs `ServicioForm` from US1; independent of US2 markup

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Form widgets before (or parallel with) template
- `clean()` rules before claiming conflict story done
- Story complete before next priority if working sequentially

### Parallel Opportunities

- T002, T003, T004 in parallel (different files)
- T007 and T008 in parallel after T006
- After Phase 2, different people can take US3 (`views.py` / `templo.html`) vs US4 (`forms.py`) vs US2 (`edit_servicios.html` lower card) if US1 template/form is already in place
- Do **not** parallelize tasks that edit the same file (`misas/tests.py`, `misas/forms.py`, `misas/templates/misas/edit_servicios.html`)

---

## Parallel Example: User Story 1

```bash
# After T006 tests exist and fail:
Task: "Apply Bootstrap widgets on ServicioForm in misas/forms.py"
Task: "Restyle upper create card in misas/templates/misas/edit_servicios.html"
```

## Parallel Example: Foundational

```bash
Task: "Set LOGIN_URL in site1/settings.py"
Task: "Include contrib.auth.urls in site1/urls.py"
Task: "Create misas/templates/registration/login.html"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: authenticated create + styled upper form
5. Continue US2–US4 before calling the feature done (login wall and overlap are P1)

### Incremental Delivery

1. Setup + Foundational → login page exists, tests can authenticate
2. US1 → styled form + valid/invalid create (MVP demo)
3. US2 → lower list + empty state
4. US3 → anonymous cannot mutate
5. US4 → duplicate/overlap rejected
6. Polish → `manage.py test misas` + browser pass

### Parallel Team Strategy

1. Team completes Setup + Foundational together
2. Then: A = US1 then US2 (templates), B = US3 (auth), C = US4 (form `clean`) after US1 form exists

---

## Notes

- [P] tasks = different files, no dependencies
- No new models or migrations
- Parish-level authorization is out of scope (FR-010)
- Do not add delete/edit of existing services
- Commit after each task or logical group
- Stop at checkpoints to validate the story independently
