# Contract: Alta y edición de ficha del templo

Internal Django HTML contract. Not a public JSON API.

## Routes

| Method | Path | Name | Auth | Result |
|--------|------|------|------|--------|
| GET | `/misas/templo/nuevo/` | `misas:nuevo_templo` | Anonymous | `302` to login with `next` pointing at this URL. Body MUST NOT include the create form. |
| GET | `/misas/templo/nuevo/` | `misas:nuevo_templo` | Authenticated | `200`. Spanish create form: nombre, dirección, alias, foto. Same visual language as the directory. |
| POST | `/misas/templo/nuevo/` | `misas:nuevo_templo` | Anonymous | `302` to login. MUST NOT insert a `Templo`. |
| POST | `/misas/templo/nuevo/` | `misas:nuevo_templo` | Authenticated | CSRF required. `multipart/form-data`. Valid → persist one `Templo` and `302` to `misas:templo` for that id. Invalid → `200` with Spanish form errors, no row (or no new row). |
| GET | `/misas/templo/<uuid:id_templo>/editar/` | `misas:editar_templo` | Anonymous | `302` to login with `next` pointing at this URL. Body MUST NOT include the edit form. |
| GET | `/misas/templo/<uuid:id_templo>/editar/` | `misas:editar_templo` | Authenticated | `200`. Form filled with current nombre, dirección, alias; current photo preview if any. Unknown UUID → `404`. |
| POST | `/misas/templo/<uuid:id_templo>/editar/` | `misas:editar_templo` | Anonymous | `302` to login. MUST NOT update the `Templo`. |
| POST | `/misas/templo/<uuid:id_templo>/editar/` | `misas:editar_templo` | Authenticated | CSRF required. `multipart/form-data`. Valid → update that templo and `302` to `misas:templo`. Invalid → `200` with Spanish errors; existing row unchanged. Unknown UUID → `404`. |
| GET | `/accounts/login/` | `login` | Anonymous | `200`. Existing Spanish sign-in. After success, return via `next`. |

Login uses Django auth already mounted at `/accounts/`. `LOGIN_URL` stays `/accounts/login/`.

## POST body (form)

| Field | Required | Notes |
|-------|----------|--------|
| `csrfmiddlewaretoken` | yes | Existing CSRF middleware stays on. |
| `nombre` | yes | Text. |
| `direccion` | yes | Text. |
| `alias` | no | Text; empty allowed. |
| `imagen` | no | File. JPEG/PNG/WebP, ≤ 5 MB. Omit to keep current photo (edit) or create without photo. |

Create MUST NOT accept a client-supplied templo id. Edit templo comes from the URL, not the body.

## Validation outcomes

| Situation | Persist? | User-visible |
|-----------|----------|--------------|
| Valid create, with or without photo | yes (insert) | Redirect to public ficha; photo or placeholder as stored |
| Valid edit of one or more text fields, no new file | yes (update text only) | Redirect to ficha; photo unchanged |
| Valid edit with a new image | yes (update photo; text as submitted) | Redirect to ficha; new photo shown |
| Missing nombre or dirección | no | Spanish field error; create does not insert; edit leaves prior data |
| Non-image or disallowed extension | no | Spanish error; no new templo / no change to existing photo |
| File larger than 5 MB | no | Spanish error; no persist |
| Empty alias | yes if other required fields valid | Templo saved without another known name |

## Public pages (access unchanged)

| Route | Auth | Photo behavior |
|-------|------|----------------|
| `misas:index` | Public | Card uses `templo.imagen` when present; otherwise existing placeholder. MUST NOT 404 the image. |
| `misas:templo` | Public | Header uses the same rule. MUST include a link to `misas:editar_templo`. Following that link while anonymous hits the login contract above. “Agregar Servicio” unchanged. |

## Media

| Item | Contract |
|------|----------|
| Public image URL | `templo.imagen.url` when the field is set |
| Debug serving | `GET /media/templos/...` returns the file when `DEBUG` is on |
| Placeholder | Rendered when `imagen` is empty; never an `<img>` with a missing src |
