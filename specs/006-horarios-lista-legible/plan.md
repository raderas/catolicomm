# Implementation Plan: Horarios de servicios como lista legible

**Branch**: `006-horarios-lista-legible` | **Date**: 2026-09-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/006-horarios-lista-legible/spec.md`

## Summary

On the public temple ficha and the servicios editor list, render each day’s start times as a comma-separated Spanish 12-hour list (`8:00 a. m., 10:00 a. m., 6:00 p. m.`). Stop dumping the Python list (`['08:00', '10:00']`). Convert only at display time; `Servicio.hora_inicio` stays a `TimeField` with no migration. The create form and parish listing cards are out of scope.

## Technical Context

**Language/Version**: Python 3.12, Django 6.1

**Primary Dependencies**: Django (`Templo.get_servicios()`, templates), Bootstrap 5 + project classes in `misas/templates/base.html`

**Storage**: Unchanged. `Servicio.hora_inicio` remains `TimeField`. No new tables or migrations.

**Testing**: Django `TestCase` / `Client` in `misas/tests.py` (ficha + editor list, midnight/noon/single/multi), plus a browser pass of both screens. Existing service-editor POST tests stay green (form still posts `HH:MM`).

**Target Platform**: Django web app (desktop and mobile browsers)

**Project Type**: Single Django project (`site1`) + `misas` app

**Performance Goals**: Low-traffic parish screens; formatting a handful of times per GET is in-process, no extra queries.

**Constraints**: Spanish UI (`lang="es"`); `a. m.` / `p. m.` with spaces, no leading hour zero; no 24-hour values in those lists; no English `AM`/`PM`; no new design system; thin views; do not invent or drop hours; do not change stored times or the alta form.

**Scale/Scope**: Two templates that already iterate `get_servicios()`, one display helper, tests. Typical templo: a few service types, a few hours per day.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | How this plan complies |
|-----------|--------|------------------------|
| I. Idiomatic Django | Pass | Reuse `Templo.get_servicios()` and existing function views. One small display helper next to that method. No new app, service layer, or CBVs. Templates only join and show the formatted list. |
| II. Critical-path tests | Pass | Tests for public ficha and editor list: comma-separated 12-hour copy, no list repr, no 24-hour dump, single hour, midnight/noon, order preserved. Browser check supplements. Existing create/overlap tests stay green. |
| III. Existing Spanish UI | Pass | Same cards/tabs/list-group. Copy stays Spanish. Markers are `a. m.` / `p. m.`, not English `AM`/`PM`. No new design system. |
| IV. Django security defaults | Pass | No new mutating routes. Public ficha stays public (FR-007). Editor stays `login_required`. CSRF unchanged. |
| V. Community-accurate data | Pass | Hours come from stored `Servicio.hora_inicio`. Helper only reformats; join does not drop or invent. Empty templo keeps existing empty copy. |
| Stack / YAGNI | Pass | Python 3.12 / Django 6.1. No locale package, no JS formatter, no schema change. |

Post-design re-check: same results. Contract is HTML GET of ficha and editor list, not a JSON API. Complexity table empty.

## Project Structure

### Documentation (this feature)

```text
specs/006-horarios-lista-legible/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── horarios-legibles.md
└── tasks.md              # /speckit-tasks — not created here
```

### Source Code (repository root)

```text
misas/
├── models.py                          # display helper; get_servicios() lists formatted start times
├── tests.py                           # ficha + editor list format cases; keep POST HH:MM
└── templates/misas/
    ├── templo.html                    # join hours; stop dumping the list object
    └── edit_servicios.html            # join already present; show 12-hour strings
site1/
manage.py
```

**Structure Decision:** Stay in the existing Django monolith. Touch the derived schedule helper and the two templates that print day hours. Do not add `frontend/`, a second app, or migrations.

## Complexity Tracking

> No constitution violations.

## Phase 0 & Phase 1 outputs

- [research.md](./research.md) — list dump vs join, 12-hour helper vs Django `TIME_FORMAT`, storage unchanged
- [data-model.md](./data-model.md) — display mapping from `TimeField` to lista de horas; no schema change
- [contracts/horarios-legibles.md](./contracts/horarios-legibles.md) — GET ficha and GET editor list HTML
- [quickstart.md](./quickstart.md) — `manage.py test` and browser pass
