# Quickstart: Foto y edición de datos del templo

Validate this feature after implementation. Field rules are in [data-model.md](./data-model.md); HTTP/HTML behavior is in [contracts/templo-ficha.md](./contracts/templo-ficha.md).

## Prerequisites

- Python 3.12, project virtualenv, dependencies from `requirements.txt` (includes Pillow)
- Env vars already used by the app (`DJANGO_SECRET_KEY`, database settings)
- Apply migrations so `Templo.imagen` exists: `python manage.py migrate`
- At least one Django user (`python manage.py createsuperuser` if needed)

## Automated checks

From the repo root:

```bash
python manage.py test misas
```

Expect existing service-editor tests to keep passing, plus coverage of:

- Anonymous GET/POST of `/misas/templo/nuevo/` and `/misas/templo/<id>/editar/` → redirect to login; no insert/update
- Authenticated GET create → `200` with nombre, dirección, alias, imagen, CSRF
- Authenticated POST create without photo → one `Templo`; public ficha shows placeholder
- Authenticated POST create with a tiny valid PNG/JPEG → templo has `imagen`; public ficha/list HTML includes that file URL
- Authenticated POST create with `.txt` or oversized file → no insert
- Authenticated GET edit → `200` with current values
- Authenticated POST edit changing only `nombre` → name updates; dirección, alias, `imagen` unchanged
- Authenticated POST edit with a new image and same text → photo replaced; text unchanged if resubmitted as-is
- Authenticated POST edit with empty nombre → no update
- Unknown templo UUID on edit → `404`
- Public index and ficha remain reachable without a session

## Manual browser pass (required for UI)

1. Sign out. Open `/misas/templo/nuevo/` and an edit URL. Confirm you never see the form and are asked to sign in.
2. Sign in from that redirect. Confirm you land back on the requested screen.
3. Create a templo with name, address, and a phone photo. Confirm the public ficha and the listing card show that image (not a broken image, not only the church icon).
4. Create another templo without a photo. Confirm the placeholder icon, not a broken `<img>`.
5. From a public ficha, follow **Editar templo**. Change only the name; save. Confirm the ficha shows the new name and the same photo (or same placeholder).
6. Edit again: attach a different image without changing the name. Confirm the ficha shows the new photo.
7. Try a PDF or `.txt` as the photo; confirm a Spanish error and no data loss.
8. Confirm create and edit screens use the same cream/gold cards and gold primary button as the parish listing — not `form.as_p` unstyled.
9. Open the public ficha and listing signed out; names, addresses, and photos still show.

## Done when

Tests above pass and the browser pass matches the spec (upload on create, dedicated edit screen, login wall, public photo or placeholder).
