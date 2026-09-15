---
description: "Task list for horarios de servicios como lista legible"
---

# Tasks: Horarios de servicios como lista legible

**Input**: Design documents from `/specs/006-horarios-lista-legible/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included. Spec independent tests, constitution II (temple detail and service schedules), and `quickstart.md`. Write tests first and confirm they fail before implementation. Do not weaken existing create/overlap, ficha/photo, navbar, or cuenta coverage in `misas/tests.py`. Keep POSTing `hora_inicio` as `"HH:MM"` / `time(...)`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Existing Django monolith: `site1/` project, `misas/` app (not `src/`).

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Shared test helpers. The Django project, `Templo.get_servicios()`, public ficha, and servicios editor already exist. No new packages. No migrations.

- [X] T001 Add a new `TestCase` helper class in `misas/tests.py` (do not change behavior of existing temple/service/navbar/cuenta classes) that builds a `Templo` (`nombre`, `direccion` required), an anonymous `Client`, a logged-in editor `Client`, and helpers to create `Servicio` rows with stored `hora_inicio` as `time(...)`. Include a same-day, same-tipo set with `08:00`, `10:00`, and `18:00`, plus ficha (`misas:templo`) and editor (`misas:templo_servicios`) URL helpers

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Display helper and derived list. Do **not** join in `templo.html` yet (that is US1). Do **not** migrate `Servicio.hora_inicio`.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Add a display helper next to `Templo.get_servicios()` in `misas/models.py` that maps stored `datetime.time` to `hora_display` per [data-model.md](./data-model.md): `00:MM` → `12:MM a. m.`; `01:MM`–`11:MM` → `{h}:{MM} a. m.` (no leading zero); `12:MM` → `12:MM p. m.`; `13:MM`–`23:MM` → `{h-12}:{MM} p. m.`. Minutes always two digits. Suffix exactly `a. m.` or `p. m.` (spaces in the marker). MUST NOT emit `AM`, `PM`, `a.m.`, or 24-hour `H:i`. Call it from `get_servicios()` so each list value is `hora_display`, not `strftime("%H:%M")`. Append order MUST stay the current `servicio_set` loop. Count of displays for a tipo+día MUST equal that templo’s `Servicio` rows for that tipo and weekday. MUST NOT write `hora_inicio`. No new field; `hora_inicio` stays required `TimeField`
- [X] T003 Update existing editor-list assertions in `misas/tests.py` that expect 24-hour tokens in the lower list HTML (notably `"18:00"`) so they expect the 12-hour `hora_display` (`6:00 p. m.`). Keep POST bodies as `"10:00"` / `time(10, 0)`. Empty `get_servicios() == {}` MUST still hold. Do not change `misas/templates/misas/templo.html` yet

**Checkpoint**: Foundation ready — `get_servicios()` returns Spanish 12-hour strings; storage and alta POST unchanged; ficha may still dump the Python list until US1

---

## Phase 3: User Story 1 - Leer los horarios del templo sin notación de programación (Priority: P1) 🎯 MVP

**Goal**: Anonymous GET of the public ficha shows each day’s start times as a comma-separated 12-hour list (`8:00 a. m., 10:00 a. m., 6:00 p. m.`), without brackets, quotes, or 24-hour values.

**Independent Test**: Visitor opens `/misas/templo/<uuid>/` for a templo with 08:00, 10:00, and 18:00 the same day and reads `8:00 a. m., 10:00 a. m., 6:00 p. m.` next to the weekday. No `['08:00'` and no `18:00` in that list.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T004 [US1] Add failing `Client` tests in `misas/tests.py` for anonymous GET `misas:templo`: same-day `08:00`/`10:00`/`18:00` HTML contains exact `8:00 a. m., 10:00 a. m., 6:00 p. m.`; MUST NOT contain `[` wrapping hours, `'` around hours, `08:00`, `18:00`, `8:00 AM`, or `8:00 a.m.`; single stored `08:00` contains `8:00 a. m.` and MUST NOT contain a trailing comma after that hour; stored `00:00` contains `12:00 a. m.`; stored `12:00` contains `12:00 p. m.`; after GET, `Servicio.hora_inicio` is still the original `time`; unknown UUID → `404`; GET `misas:index` is not required to show this list

### Implementation for User Story 1

- [X] T005 [US1] In `misas/templates/misas/templo.html`, render each day’s hours with `{{ horas|join:", " }}` (comma + space) instead of `{{ horas }}`. Keep tipo tabs, day labels, and list-group markup. Do not change `misas/templates/misas/index.html`. Do not add chips or extra spans per hour

**Checkpoint**: Public ficha shows a readable 12-hour list. Editor list may already show 12-hour strings via `get_servicios()`; US2 confirms join + parity

---

## Phase 4: User Story 2 - Confirmar los mismos horarios legibles al editar servicios (Priority: P1)

**Goal**: Authenticated GET of the servicios editor lower list uses the same comma-separated `a. m.` / `p. m.` strings as the ficha. Empty templo keeps Spanish empty copy. Create form time widgets unchanged.

**Independent Test**: Same templo as US1: logged-in GET `/misas/templo/<uuid>/servicios/` lower list matches the ficha hour list. Form still posts `HH:MM`.

### Tests for User Story 2

- [X] T006 [US2] Add failing tests in `misas/tests.py`: authenticated GET `misas:templo_servicios` lower list contains the same `8:00 a. m., 10:00 a. m., 6:00 p. m.` (or single-hour / midnight / noon strings) as GET `misas:templo` for that templo; MUST NOT contain Python list `repr` in the lower list; templo with no servicios still shows the Spanish empty copy and `get_servicios() == {}`; GET includes `name="hora_inicio"` on the create form; valid POST `hora_inicio="10:00"` still persists `time(10, 0)`; anonymous GET editor still `302` to login

### Implementation for User Story 2

- [X] T007 [US2] In `misas/templates/misas/edit_servicios.html`, keep `{{ horas|join:", " }}` on the registered-services list (comma + space). Do not change create-form `hora_inicio` / `hora_fin` widgets or labels. Empty state copy stays. MUST NOT add service edit/delete controls

**Checkpoint**: Ficha and editor list match; alta still stores `TimeField`; listing cards untouched

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Full-suite tests, browser pass, lint, no scope creep

- [X] T008 Run `python manage.py test misas` from repo root until US1–US2 cases in `specs/006-horarios-lista-legible/quickstart.md` pass (existing service-editor POST/overlap, ficha/photo, navbar, and cuenta tests MUST stay green)
- [X] T009 Browser-pass `specs/006-horarios-lista-legible/quickstart.md` against `misas/templates/misas/templo.html` and `misas/templates/misas/edit_servicios.html`: comma-separated `a. m.` / `p. m.` on ficha and editor, afternoon as `6:00 p. m.` not `18:00`, create form unchanged, no extra servicio after reload
- [X] T010 Confirm out of scope: no migration under `misas/migrations/` for this feature; `misas/templates/misas/index.html` listing cards unchanged; `{% csrf_token %}` remains on the editor create form; `Servicio.hora_inicio` still `TimeField`
- [X] T011 Run `pre-commit run ruff-check --all-files` and `pre-commit run ruff-format --all-files` after Python edits; fix reported issues in `misas/models.py` and `misas/tests.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup — BLOCKS all user stories (`get_servicios()` display strings)
- **User Stories (Phase 3+)**: All depend on Foundational
  - Sequential for one implementer: US1 → US2 (shared `get_servicios()`; US2 template already joins)
- **Polish (Phase 5)**: Depends on US1–US2 complete

### User Story Dependencies

- **User Story 1 (P1)**: After Phase 2. MVP. Ficha join. No dependency on US2
- **User Story 2 (P1)**: After Phase 2. Needs the same `hora_display` values. Independently testable as editor GET vs ficha GET

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Helper + `get_servicios()` (Phase 2) before ficha join
- Story complete before next priority if working sequentially

### Parallel Opportunities

- After T001, T002 is sequential with T003 (same `misas/tests.py` / `misas/models.py` coupling)
- T004 tests before T005 template
- T006 tests before T007 (T007 may be a no-op confirm if join already exists)
- Do **not** parallelize tasks that edit the same file (`misas/tests.py`, `misas/models.py`)

---

## Parallel Example: User Story 1

```bash
# After T004 tests exist and fail:
Task: "Join hours with comma+space in misas/templates/misas/templo.html"
```

## Parallel Example: Foundational

```bash
# After T001:
Task: "Add 12-hour display helper and wire get_servicios() in misas/models.py"
# Then (same tests.py as existing assertions):
Task: "Retarget existing 18:00 list assertions in misas/tests.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: public ficha shows `8:00 a. m., 10:00 a. m., 6:00 p. m.`
5. Continue US2 before calling the feature done (editor parity is also P1)

### Incremental Delivery

1. Setup + Foundational → helper + `get_servicios()` 12-hour strings
2. US1 → ficha join (MVP demo)
3. US2 → editor list matches ficha; form unchanged
4. Polish → `manage.py test misas` + browser pass + ruff

### Parallel Team Strategy

1. Team completes Setup + Foundational together
2. Then: A = US1 (`templo.html`), B = US2 tests (`misas/tests.py`) after agreeing T003 already updated shared editor assertions

---

## Notes

- [P] tasks = different files, no dependencies
- No migrations and no `User` / `Templo` schema changes
- Display only: `a. m.` / `p. m.`, no leading hour zero, comma + space
- Do not format `index.html` próxima misa
- Do not mutate `Servicio.hora_inicio` on GET
- Commit after each task or logical group
- Stop at checkpoints to validate the story independently
