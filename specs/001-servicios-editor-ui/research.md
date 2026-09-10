# Research: Editor de servicios del templo

## 1. Authentication for the editor page

**Decision:** Protect `templo_servicios_edit` with Django's `login_required`. Include `django.contrib.auth.urls` at `/accounts/` and set `LOGIN_URL` to the built-in login view. Add one Spanish login template that extends `base.html`. After sign-in, Django's `next` parameter returns the editor to the same temple.

**Rationale:** The app already has `django.contrib.auth` and the admin user store. There is no public login route today (`site1/urls.py` only mounts `misas/` and `admin/`). Sending parish editors to `/admin/login/` would leak a different visual system (constitution III). `contrib.auth.urls` plus a themed template is the smallest change that satisfies FR-009 without a new identity product.

**Alternatives considered:**
- `/admin/login/` as `LOGIN_URL` — works, but the admin chrome is not the cream/gold directory.
- Custom user model or OAuth — out of scope; spec assumes the existing account system.
- Parish-scoped authorization — deferred by spec FR-010; constitution IV is documented as a follow-up, not this feature.

## 2. Overlap and duplicate validation placement

**Decision:** Enforce FR-013 / FR-014 in `ServicioForm.clean()` (and a helper used by tests). Do not add a database unique constraint or a new model. Treat intervals as half-open `[hora_inicio, hora_fin)` so adjacent slots (10:00–11:00 then 11:00–12:00) are valid. If the existing service has no `hora_fin`, only the exact duplicate rule (same temple, type, weekday, `hora_inicio`) applies. If the new service has no `hora_fin`, treat it as a point at `hora_inicio` against existing intervals that do have `hora_fin`.

**Rationale:** Overlap is interval logic, not equality, so a unique index cannot express it. Constitution I wants thin views and `ModelForm` for create/edit. Form-level validation shows Spanish messages next to the form (FR-015) and never calls `save()` on invalid data (FR-004). No migration keeps the change local (YAGNI).

**Alternatives considered:**
- Unique together on `(templo, tipo_servicio, dia_de_semana, hora_inicio)` — covers duplicates only; overlap still needs form logic; extra migration for a partial win.
- Model `clean()` / `save()` override only — valid, but the editor already uses `ServicioForm`; putting rules there keeps the view thin and messages on the form.
- Database exclusion constraints (`tstzrange`) — PostgreSQL-specific, heavier than this feature needs.

## 3. Editor UI restyle

**Decision:** Restyle `misas/templates/misas/edit_servicios.html` in place. Reuse `templo_header.html`. Upper card: create form with Bootstrap 5 `form-select` / `form-control`, `btn btn-gold`, CSRF kept. Lower card: existing services from `templo.get_servicios()`, grouped by type, with an explicit empty state in Spanish. Widget CSS classes set on the `ModelForm` so the template stays simple.

**Rationale:** Spec requires the listing-page visual language (cards, cream/gold, serif titles) and forbids a new design system (constitution III). `index.html` and `base.html` already define `bg-surface`, `border-subtle`, `btn-gold`, `form-control`. `templo.html` already groups `get_servicios()` by type; the editor list should show the same real data (constitution V) without inventing a second grouping API.

**Alternatives considered:**
- New template/name or a SPA — drive-by structure, forbidden.
- Delete buttons in the lower list — out of spec.
- Duplicating schedule data in the view instead of `get_servicios()` — risks drift from public detail.

## 4. Tests and browser verification

**Decision:** Expand `misas/tests.py` with Django `TestCase` + `Client` for auth redirects, valid create, duplicate, overlap, adjacent-allowed, different-type-allowed, empty state, and missing temple. Supplement with a browser pass of the editor (form + list + login redirect) before calling the work done.

**Rationale:** Constitution II requires tests when create/edit forms and service schedules change. `misas/tests.py` is empty today; an empty module does not waive the rule. Browser verification is required by the constitution workflow for UI changes.

**Alternatives considered:**
- Browser-only checks — not allowed as the sole critical-path evidence.
- pytest-django — extra runner; the project already uses Django's test runner.

## 5. Persistence and schema

**Decision:** No model field changes and no migration. Keep using the existing `Templo` / `Servicio` tables and the project's current database settings.

**Rationale:** Duplicate and overlap rules are validation, not new attributes. The constitution names SQLite as the default until a migration is ratified; this project already points at PostgreSQL via environment variables. This feature does not change that.

**Alternatives considered:**
- Switching this feature to SQLite — unrelated to the editor UI; would be a drive-by infra change.
