# Implementation Plan: Enlace de Facebook y verificación del templo

**Branch**: `004-templo-facebook-verificado` | **Date**: 2026-09-14 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-templo-facebook-verificado/spec.md`

## Summary

Add an optional Facebook URL on temple create/edit and a `verificado` flag that always starts false. Show the Facebook icon + address, unverified asterisk/notes, the festivities disclaimer, and a staff-only verify control in the existing shared `templo_header.html` (public ficha and services editor). Any valid save of temple details or of a service clears `verificado` so a site admin can mark it again.

## Technical Context

**Language/Version**: Python 3.12, Django 6.1

**Primary Dependencies**: Django (views, `ModelForm`, `URLField`, `BooleanField`, `contrib.auth`), Bootstrap 5 + Bootstrap Icons already in `misas/templates/base.html`

**Storage**: PostgreSQL via env (SQLite in-memory for tests). One generated migration: `Templo.facebook` (`URLField`, optional) and `Templo.verificado` (`BooleanField`, default `False`).

**Testing**: Django `TestCase` / `Client` in `misas/tests.py` (keep existing ficha, photo, and service-editor tests), plus a browser pass of Facebook display, verify/revoke, asterisk/notes, and staff-only control

**Target Platform**: Django web app (desktop and mobile browsers)

**Project Type**: Single Django project (`site1`) + `misas` app

**Performance Goals**: Low-traffic parish screens; full page round-trip after save or verify is acceptable. No extra queries beyond one `Templo` update when revoking or toggling verification.

**Constraints**: Spanish UI (`lang="es"`); CSRF stays on; no new design system; views/forms stay thin; Facebook optional; `verificado` excluded from `TemploForm`; only `is_staff` may verify; listing cards stay unchanged; no service delete/edit UI in this feature; no parish-ownership model

**Scale/Scope**: Two fields on `Templo`, extend `TemploForm` and create/edit templates, one POST verify route, header markup + notes, revoke on existing templo/servicio save paths, tests. Typical directory: dozens of temples.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | How this plan complies |
|-----------|--------|------------------------|
| I. Idiomatic Django | Pass | Extend existing `Templo` / `TemploForm`. Function views matching `templo_edit` / `templo_servicios_edit`. Generated migration. No new app or service layer. |
| II. Critical-path tests | Pass | Tests for Facebook create/edit/display, invalid URL, default unverified, staff verify / non-staff 403, revoke on ficha and service save, invalid save does not revoke, asterisk + notes. Browser check supplements, does not replace. Existing tests stay green (updated only where the create form now includes Facebook). |
| III. Existing Spanish UI | Pass | Facebook field and notes in existing cards / `form-control` / `btn-gold`. Display and verify live in `templo_header.html` (already included by ficha and servicios). Copy in Spanish. `bi-facebook` from the icons already loaded. |
| IV. Django security defaults | Exception (justified, same as 002) | CSRF remains. Ficha and service **edits** stay authenticated-any-user per existing FR (no parish ownership). **Verification** is staff-only (`is_staff` → 403 otherwise). Secrets stay in env. |
| V. Community-accurate data | Pass | Facebook and verificado come from stored `Templo` fields. Empty Facebook shows nothing (no fabricated link). Unverified temples show the pending-validation note rather than a Verificado mark. Service schedules are unchanged except the existing create path, which also revokes verification. |
| Stack / YAGNI | Pass | Python 3.12 / Django 6.1. No new packages. No service modify/delete screens (those mutations do not exist; only the existing create is hooked). Listing cards out of spec. |

Post-design re-check: same results. Contracts are HTML routes, not a new JSON API. Complexity table records only the IV exception (parish ownership), which this feature does not expand.

## Project Structure

### Documentation (this feature)

```text
specs/004-templo-facebook-verificado/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── facebook-verificado.md
└── tasks.md              # /speckit-tasks — not created here
```

### Source Code (repository root)

```text
misas/
├── models.py                   # Templo.facebook, Templo.verificado; revoke helper
├── forms.py                    # TemploForm: add facebook (not verificado)
├── views.py                    # templo_verificar POST; revoke after templo_edit / servicio save
├── urls.py                     # verificar_templo route
├── admin.py                    # list_display: facebook, verificado
├── tests.py                    # Facebook, verify, revoke, header notes
├── migrations/                 # generated: facebook + verificado
└── templates/misas/
    ├── templo_header.html      # Facebook link, asterisk, notes, staff verify form
    ├── newtemplo.html          # Facebook field via form (same grid)
    └── edit_templo.html        # Facebook field via form (same grid)
manage.py
```

**Structure Decision:** Stay in the existing Django monolith. Touch model/form/views/urls, the shared header template, and the two ficha forms that already loop field widgets. Do not add `frontend/` or a second app. Do not change listing (`index.html`) in this iteration.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Constitution IV parish authorization not implemented for ficha/service edits | Unchanged from 001/002: any authenticated user may edit any temple this iteration | Building user–templo ownership now would expand scope beyond Facebook + verification |

## Phase 0 & Phase 1 outputs

- [research.md](./research.md) — URLField, staff verify POST, header UI, revoke hooks
- [data-model.md](./data-model.md) — `Templo.facebook` / `verificado` rules and state
- [contracts/facebook-verificado.md](./contracts/facebook-verificado.md) — create/edit Facebook, public header, verify POST, revoke
- [quickstart.md](./quickstart.md) — `manage.py test` and browser pass
