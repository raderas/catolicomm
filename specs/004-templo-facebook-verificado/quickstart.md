# Quickstart: Enlace de Facebook y verificación del templo

Validate this feature after implementation. Field rules are in [data-model.md](./data-model.md); HTTP/HTML behavior is in [contracts/facebook-verificado.md](./contracts/facebook-verificado.md).

## Prerequisites

- Python 3.12, project virtualenv, dependencies from `requirements.txt`
- Env vars already used by the app (`DJANGO_SECRET_KEY`, database settings)
- Apply migrations so `Templo.facebook` and `Templo.verificado` exist: `python manage.py migrate`
- One regular user and one **staff** user (`is_staff=True`; `createsuperuser` is enough for staff)

## Automated checks

From the repo root:

```bash
python manage.py test misas
```

Expect existing ficha, photo, navbar, and service-editor tests to keep passing, plus coverage of:

- Authenticated GET create/edit includes `name="facebook"` and CSRF; does not include a verify checkbox
- Authenticated POST create with `https://www.facebook.com/parroquia` → row has that URL, `verificado=False`; public ficha HTML includes `bi-facebook` and the address as a link
- Authenticated POST create without Facebook → no `bi-facebook` / no empty Facebook href on ficha or servicios header
- Authenticated POST create with `facebook.com/parroquia` (no scheme) → stored as `https://facebook.com/parroquia`
- Authenticated POST with `facebook=no es una url` → no insert (create) / no update (edit); Spanish error
- POST create with extra `verificado=1` still yields `verificado=False`
- Staff POST `misas:verificar_templo` `verificado=1` then `0` updates the flag; ficha/servicios header matches (Verificado vs `*` + validation note)
- Non-staff POST verify → `403`, flag unchanged; anonymous POST → login redirect, flag unchanged; GET verify → `405`
- Valid edit of a verified templo (e.g. change Facebook or nombre) → `verificado=False` and pending UI
- Valid servicio create on a verified templo → `verificado=False` on the same `200`
- Invalid templo or servicio POST on a verified templo → flag stays `True`
- Every ficha/servicios header contains the festivities sentence

## Manual browser pass (required for UI)

1. Sign in as a regular editor. Create a templo with a Facebook URL. On the public ficha, confirm icon + address; click opens Facebook in a new tab; name has `*`; pending-validation note and festivities note are at the foot of the header. Confirm the listing card did **not** gain Facebook/asterisk.
2. Open **Agregar Servicio** for that templo. Confirm the same header (Facebook, asterisk, both notes). Add a valid service (temple is still unverified).
3. Sign out. Open the ficha. Facebook link, asterisk, and notes still show. No verify button.
4. Sign in as staff. On the ficha, **Marcar como verificado**. Confirm “Verificado”, no asterisk, no pending note, festivities note remains. Repeat from the servicios screen: **Quitar verificación** then mark again.
5. As a regular editor, edit the verified templo (change Facebook or address) and save. Confirm the ficha is unverified again (asterisk + pending note). Ask staff to re-mark.
6. As staff, mark verified, then as editor add another service. Confirm verification clears on that servicios response.
7. Submit an invalid Facebook URL on edit; confirm Spanish error and that a verified templo would stay verified if you repeat this on a marked templo.
8. Confirm create/edit still use cream/gold cards; header still matches the directory (no new visual system).

## Done when

Tests above pass and the browser pass matches the spec (Facebook on alta/edición, header icon+address, staff-only verify on the shared block, revoke on ficha/servicio save, asterisk and Spanish notes).
