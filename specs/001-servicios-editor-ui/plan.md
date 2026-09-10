# Implementation Plan: Editor de servicios del templo

**Branch**: `001-servicios-editor-ui` | **Date**: 2026-09-10 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-servicios-editor-ui/spec.md`

## Summary

Restyle the temple service editor so logged-in users see a Bootstrap 5 create form in the upper card (same cream/gold language as the parish listing) and existing services grouped in a lower card, including an empty state. Anonymous visitors are sent to a Spanish login and returned via `next`. `ServicioForm` rejects duplicate start times and interior overlaps of the same type/day (half-open intervals; adjacent slots allowed) and never inserts those rows.

## Technical Context

**Language/Version**: Python 3.12, Django 6.1

**Primary Dependencies**: Django (views, `ModelForm`, `contrib.auth`), Bootstrap 5 + project classes in `misas/templates/base.html`

**Storage**: Existing `Templo` / `Servicio` tables. Project database is already configured (PostgreSQL via env). No new migration for this feature.

**Testing**: Django `TestCase` / `Client` in `misas/tests.py`, plus a browser pass of the editor and login redirect

**Target Platform**: Django web app (desktop and mobile browsers)

**Project Type**: Single Django project (`site1`) + `misas` app

**Performance Goals**: Editor is a low-traffic parish screen; a full page round-trip after save is acceptable. Overlap checks run against that temple’s existing services only.

**Constraints**: Spanish UI (`lang="es"`); CSRF stays on; no new design system; views/forms stay thin; no delete/edit of existing services; no parish-ownership model in this iteration

**Scale/Scope**: One editor template, one login template, form validation, `login_required` on one route, tests for auth and schedule conflicts. Typical temple has a small number of weekly services.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | How this plan complies |
|-----------|--------|------------------------|
| I. Idiomatic Django | Pass | Keep `templo_servicios_edit` + `ServicioForm`. Overlap/duplicate in `ServicioForm.clean()`. `login_required` only. No new app, service layer, or CBV unless it clearly fits. |
| II. Critical-path tests | Pass | Tests for editor GET/POST, empty list, duplicate, overlap, adjacent-allowed, auth redirect. Browser check supplements, does not replace. |
| III. Existing Spanish UI | Pass | Restyle `edit_servicios.html` with existing `card` / `btn-gold` / `form-control` patterns from `index.html` and `base.html`. Login template extends `base.html`. |
| IV. Django security defaults | Exception (justified) | CSRF remains. Editor is authenticated. **Parish-level authorization is out of spec (FR-010)**; any logged-in user may edit any temple. Follow-up: user–templo link. Secrets stay in env. |
| V. Community-accurate data | Pass | Lower list uses `templo.get_servicios()`. Empty temples show absence, not a fake mass. Conflicts do not write a row. |
| Stack / YAGNI | Pass | Python 3.12 / Django 6.1. No schema change. No extra JS framework. |

Post-design re-check: same results. Contracts are HTML routes, not a new API surface. Complexity table records only the IV exception.

## Project Structure

### Documentation (this feature)

```text
specs/001-servicios-editor-ui/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── edit-servicios.md
└── tasks.md              # /speckit-tasks — not created here
```

### Source Code (repository root)

```text
site1/
├── settings.py                 # LOGIN_URL (and related auth redirects)
├── urls.py                     # include django.contrib.auth.urls
misas/
├── views.py                    # login_required on templo_servicios_edit
├── forms.py                    # ServicioForm widgets + clean() conflicts
├── models.py                   # unchanged
├── urls.py                     # templo_servicios unchanged
├── tests.py                    # auth, create, duplicate, overlap, adjacent
└── templates/
    ├── misas/
    │   └── edit_servicios.html # form up, list/empty down
    └── registration/
        └── login.html          # Spanish auth; Django contrib.auth looks here
manage.py
```

**Structure Decision:** Stay in the existing Django monolith. Touch only settings/urls for login, `ServicioForm`, the editor view/template, tests, and a themed login template. Do not add `frontend/` or a second app.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Constitution IV parish authorization not implemented | Spec FR-010: any authenticated user may open any temple editor this iteration | Building user–templo ownership now would expand scope beyond the requested UI + login wall + overlap rules |

## Phase 0 & Phase 1 outputs

- [research.md](./research.md) — auth, validation placement, UI, tests
- [data-model.md](./data-model.md) — overlap rules, no new entities
- [contracts/edit-servicios.md](./contracts/edit-servicios.md) — GET/POST and login
- [quickstart.md](./quickstart.md) — `manage.py test` and browser pass
