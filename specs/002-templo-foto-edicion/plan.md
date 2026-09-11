# Implementation Plan: Foto y edición de datos del templo

**Branch**: `002-templo-foto-edicion` | **Date**: 2026-09-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-templo-foto-edicion/spec.md`

## Summary

Let authenticated editors attach an optional temple photo on create, and add a dedicated edit screen for nombre, dirección, alias, and/or photo. Persist the file on `Templo.imagen` (`ImageField`), drop unused `imagen_url`, and feed the public listing/ficha placeholders that already expect `templo.imagen`. Anonymous visitors hit the existing Spanish login (`next` return). After a valid save, redirect to the public ficha.

## Technical Context

**Language/Version**: Python 3.12, Django 6.1

**Primary Dependencies**: Django (views, `ModelForm`, `ImageField`, `contrib.auth`), Pillow, Bootstrap 5 + project classes in `misas/templates/base.html`

**Storage**: PostgreSQL via env (SQLite in-memory for tests). New migration: remove `Templo.imagen_url`, add `Templo.imagen`. Uploaded files under `MEDIA_ROOT/templos/`.

**Testing**: Django `TestCase` / `Client` in `misas/tests.py` (keep existing service-editor tests), plus a browser pass of create, edit, login redirect, and public photo/placeholder

**Target Platform**: Django web app (desktop and mobile browsers)

**Project Type**: Single Django project (`site1`) + `misas` app

**Performance Goals**: Low-traffic parish screens; full page round-trip after save is acceptable. Photos are a single file per templo (no gallery, no transform pipeline).

**Constraints**: Spanish UI (`lang="es"`); CSRF stays on; multipart forms for uploads; no new design system; views/forms stay thin; no delete-templo, no service-schedule edits, no parish-ownership model, no “clear photo without replace”

**Scale/Scope**: One shared `TemploForm`, restyle create template, one new edit route/template, media settings, one migration, public ficha link, tests for auth and photo/text updates. Typical directory: dozens of temples, one photo each.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | How this plan complies |
|-----------|--------|------------------------|
| I. Idiomatic Django | Pass | One `TemploForm` for create/edit. Function views matching `templo_form` / `templo_servicios_edit`. `login_required` only. `ImageField` + generated migration. No new app or service layer. |
| II. Critical-path tests | Pass | Tests for create/edit GET/POST, optional photo, invalid file, text-only edit, photo replace, auth redirect, 404. Browser check supplements, does not replace. Existing service-editor tests stay green. |
| III. Existing Spanish UI | Pass | Restyle `newtemplo.html` and add `edit_templo.html` with `card` / `btn-gold` / `form-control` from `edit_servicios.html` / `index.html` / `base.html`. Public templates keep current image/placeholder markup. |
| IV. Django security defaults | Exception (justified) | CSRF remains. Create and edit are authenticated. **Parish-level authorization is out of spec (FR-014)**; any logged-in user may edit any temple. Follow-up: user–templo link. Secrets stay in env. Uploads validated (type + 5 MB). |
| V. Community-accurate data | Pass | Public pages show the stored `imagen` or the existing empty placeholder — never a fabricated photo. Invalid uploads do not write. Services are untouched. |
| Stack / YAGNI | Pass | Python 3.12 / Django 6.1. Pillow only because `ImageField` requires it. Local `MEDIA_ROOT`; no S3, cropper, or gallery. |

Post-design re-check: same results. Contracts are HTML routes plus debug media serving, not a new JSON API. Complexity table records only the IV exception.

## Project Structure

### Documentation (this feature)

```text
specs/002-templo-foto-edicion/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── templo-ficha.md
└── tasks.md              # /speckit-tasks — not created here
```

### Source Code (repository root)

```text
site1/
├── settings.py                 # MEDIA_ROOT, MEDIA_URL
├── urls.py                     # debug static() for MEDIA
misas/
├── models.py                   # Templo.imagen ImageField; drop imagen_url
├── forms.py                    # TemploForm: fields, widgets, imagen validators
├── views.py                    # login_required create; new templo_edit
├── urls.py                     # editar_templo route
├── admin.py                    # optional: imagen on TemploAdmin (no drive-by)
├── tests.py                    # create/edit/auth/upload cases
├── migrations/                 # generated: imagen_url → imagen
└── templates/misas/
    ├── newtemplo.html          # restyle + multipart + foto
    ├── edit_templo.html        # new edit screen
    ├── templo.html             # link to editar
    ├── index.html              # unchanged markup; starts working with imagen
    └── templo_header.html      # unchanged markup; starts working with imagen
media/                          # local uploads; gitignored
manage.py
requirements.txt                # add Pillow
.gitignore                      # media/
```

**Structure Decision:** Stay in the existing Django monolith. Touch model/form/views/urls/settings for media, two templates (restyle create + new edit), one public link, tests, and a generated migration. Do not add `frontend/` or a second app.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Constitution IV parish authorization not implemented | Spec FR-014: any authenticated user may create/edit any temple this iteration | Building user–templo ownership now would expand scope beyond photo upload and ficha edit |

## Phase 0 & Phase 1 outputs

- [research.md](./research.md) — ImageField vs URL, media/Pillow, validation, views, templates, tests
- [data-model.md](./data-model.md) — `Templo.imagen` rules; `imagen_url` removed
- [contracts/templo-ficha.md](./contracts/templo-ficha.md) — create/edit GET/POST, login, public photo
- [quickstart.md](./quickstart.md) — `manage.py test` and browser pass
