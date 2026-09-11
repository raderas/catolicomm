# Data Model: Foto y edición de datos del templo

This feature changes `Templo` photo storage. It does not add tables. Django’s built-in user remains the editor identity.

## Templo

| Field | Type | Rules |
|-------|------|--------|
| `id` | UUID PK | Unchanged |
| `nombre` | char, max 100 | Required on create and edit |
| `direccion` | char, max 1000 | Required on create and edit |
| `alias` | char, max 100 | Optional; empty string allowed (`blank=True`) |
| `imagen` | optional image file | Optional; `blank=True`, `null=True`; `upload_to="templos/"` |
| `imagen_url` | — | **Removed.** Replaced by `imagen`. |

**Relationships:** one templo has many servicios (`servicio_set`). Unchanged; this feature MUST NOT create, update, or delete `Servicio` rows.

**Derived display:** public listing and ficha show `imagen` when the field has a file; otherwise the existing “sin foto” placeholder. MUST NOT invent a photo.

### Photo rules

1. **Optional:** create and edit succeed with no file. Missing photo → placeholder, never a broken image.
2. **Keep on empty upload:** if the editor saves without choosing a new file, `imagen` is unchanged (including remaining empty).
3. **Replace:** a valid new file becomes the single current photo. Previous file path is no longer referenced. Explicit “clear photo” is out of scope.
4. **Accepted types:** JPEG (`jpg`/`jpeg`), PNG, WebP. Other extensions and non-image content are invalid.
5. **Size:** files larger than **5 MB** are invalid.
6. **One current photo per templo.** No gallery.

### Text validation (form)

1. Empty `nombre` or `direccion` → invalid; do not create or overwrite.
2. `alias` may be omitted or blank.
3. Invalid photo MUST NOT persist a new templo (create) and MUST NOT change an existing templo’s fields (edit), including the previous photo.

## Editor autenticado

Django `User` (contrib.auth). Any authenticated user may create a templo and edit any existing templo (FR-014). Anonymous users never see or persist these forms. Parish-scoped ownership is **not** modeled in this iteration.

## State

Templos have no workflow states. A photo is either absent or present. Create either inserts a row or is rejected. Edit either updates the bound instance or is rejected with prior data intact.

## Media files

Uploaded bytes live under `MEDIA_ROOT/templos/`. The public URL is `MEDIA_URL` + the field’s relative path (`templo.imagen.url`). Tests may use an in-memory store; they MUST still exercise valid vs invalid files.
