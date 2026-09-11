# Research: Foto y edición de datos del templo

## 1. Persist the photo as an uploaded file, not a URL

**Decision:** Replace unused `Templo.imagen_url` (`URLField`) with `Templo.imagen` (`ImageField`, `upload_to="templos/"`, `blank=True`, `null=True`). One generated migration: remove `imagen_url`, add `imagen`. Do not keep both fields.

**Rationale:** The spec requires a file from the editor’s device, not an external link. Public templates (`index.html`, `templo_header.html`) already render `{% if templo.imagen %}{{ templo.imagen.url }}`. The URL field was never wired to those templates, so dropping it avoids two competing image sources (constitution V). `ImageField` is the idiomatic Django way to store one optional photo per templo (constitution I).

**Alternatives considered:**
- Keep `imagen_url` and paste a link — contradicts the spec (upload, not URL).
- Keep both `imagen_url` and `imagen` — two sources of truth; templates would still ignore the URL.
- Third-party storage (S3, etc.) — extra infra; YAGNI for this community app. Local `MEDIA_ROOT` is enough.

## 2. Media serving and Pillow

**Decision:** Add `Pillow` to `requirements.txt` (required by `ImageField`). Set `MEDIA_ROOT` to `BASE_DIR / "media"` and `MEDIA_URL` to `"/media/"`. In `DEBUG`, append `static(MEDIA_URL, document_root=MEDIA_ROOT)` in `site1/urls.py`. Gitignore `media/`. Production hosting of uploaded files is out of this feature (same local-disk default as today).

**Rationale:** Without Pillow, `ImageField` cannot validate images. Without `MEDIA_*` and debug serving, `{% if templo.imagen %}` would either 404 or never display. Constitution stack stays Python 3.12 / Django 6.1; this is configuration, not a new platform.

**Alternatives considered:**
- WhiteNoise / CDN for uploads — WhiteNoise is for static assets, not user media; a CDN is speculative.
- `FileField` without Pillow — would accept non-images more easily and would not match “fotografía”.

## 3. Validation: type, size, optional, no clear-without-replace

**Decision:** Validate on `TemploForm`:
- Extensions: `jpg`, `jpeg`, `png`, `webp` (`FileExtensionValidator`).
- Content: Django/`ImageField` + Pillow reject non-images.
- Size cap: **5 MB** in `clean_imagen`, Spanish error if exceeded.
- Field optional (`required=False`). Empty upload on edit must not clear an existing file.
- Widget: `ClearableFileInput` **without** showing the “clear” checkbox (or a plain `FileInput` plus a template preview). Spec: add / keep / replace only; no delete-without-replace.

**Rationale:** Spec FR-007 / FR-009 and edge cases (non-image, too large, optional). Form-level checks keep the view thin (constitution I) and put Spanish messages next to the form (FR-015). 5 MB is a typical phone photo ceiling for a directory card.

**Alternatives considered:**
- No size limit — a huge upload can stall the parish editor and fill disk.
- `ClearableFileInput` with default clear checkbox — would allow deleting the photo without a replacement, which is out of spec.
- Client-only checks — not sufficient; tests must see server-side rejection.

## 4. Create and edit views stay thin ModelForm functions

**Decision:** Reuse one `TemploForm` (`nombre`, `direccion`, `alias`, `imagen`) for both screens. Keep `templo_form` as the create view; add `templo_edit` as a function view (same style as `templo_servicios_edit`). Both: `@login_required`, bind `request.POST` and `request.FILES`, CSRF stays on. After a valid save, **redirect to the public ficha** (`misas:templo`). Invalid POST re-renders the form with errors. Unknown templo UUID → `404`.

**Rationale:** Constitution I: `ModelForm` for create/edit, thin views, match surrounding function views. Redirect to the ficha makes SC-001–SC-003 observable without a second navigation pattern. `request.FILES` is required for uploads (`enctype="multipart/form-data"`). Auth reuse: existing `LOGIN_URL` and `/accounts/login/` from 001 (FR-013).

**Alternatives considered:**
- `CreateView` / `UpdateView` — they fit, but nearby mutating screens are functions; switching only here would be a drive-by style change.
- Stay on the form after save — weaker match to “see the photo on the ficha in under two minutes”.
- Parish-scoped authorization — deferred by spec FR-014; same constitution IV follow-up as 001.

## 5. Templates and public link

**Decision:** Restyle `newtemplo.html` (create) and add `edit_templo.html` (edit) using the same cards / `form-control` / `btn-gold` / Spanish copy as `edit_servicios.html` and `index.html`. Edit template shows a preview of the current photo when present, then the file input. On the public ficha (`templo.html`), add an “Editar templo” (or equivalent) link next to “Agregar Servicio”, pointing at `misas:editar_templo`. Public listing and header keep their existing `{% if templo.imagen %}` / placeholder branches; they start working once `imagen` is a real file field.

**Rationale:** FR-012, FR-016, constitution III. The public placeholders already exist; this feature feeds them instead of inventing a second image UI.

**Alternatives considered:**
- New design system or JS cropper — forbidden / YAGNI.
- Edit-in-place on the public ficha — would mix public consult with mutation; spec asks for a dedicated edit screen.

## 6. Tests and browser verification

**Decision:** Add Django `TestCase` / `Client` coverage in `misas/tests.py` (new classes; do not weaken existing service-editor tests). Use a tiny in-memory PNG via Pillow/`SimpleUploadedFile` for valid uploads, and a `.txt` (or empty) file for rejection. Supplement with a browser pass of create, edit (text-only and photo replace), login wall, and public photo/placeholder.

**Rationale:** Constitution II: create/edit forms and temple listing/detail are critical paths. Browser checks supplement; they do not replace tests.

**Alternatives considered:**
- Browser-only verification — not allowed as the sole critical-path evidence.
- pytest-django — extra runner; the project uses `manage.py test`.
