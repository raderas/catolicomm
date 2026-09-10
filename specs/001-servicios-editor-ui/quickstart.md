# Quickstart: Editor de servicios del templo

Validate this feature after implementation. Details of overlap math are in [data-model.md](./data-model.md); HTTP/HTML behavior is in [contracts/edit-servicios.md](./contracts/edit-servicios.md).

## Prerequisites

- Python 3.12, project virtualenv, dependencies from `requirements.txt`
- Env vars already used by the app (`DJANGO_SECRET_KEY`, database settings)
- At least one Django user (create via `python manage.py createsuperuser` if needed)
- At least one `Templo` in the database

## Automated checks

From the repo root:

```bash
python manage.py test misas
```

Expect coverage of:

- Anonymous GET/POST of the editor → redirect to login, no new `Servicio`
- Authenticated GET → `200` with form + list or empty state
- Valid POST → one new `Servicio` for that templo
- Duplicate same type/day/`hora_inicio` → no insert
- Interior overlap vs a sibling with `hora_fin` → no insert
- Adjacent `10:00–11:00` then `11:00–12:00` same type → both persist
- Unknown templo UUID → `404`

## Manual browser pass (required for UI)

1. Sign out. Open `/misas/templo/<id>/servicios/`. Confirm you never see the editor and are asked to sign in.
2. Sign in. Confirm you land back on that temple’s editor.
3. Confirm the create form is the **upper** card (Bootstrap controls, gold primary button, Spanish labels) and existing services (or empty copy) are the **lower** card, visually aligned with the parish listing.
4. Create a valid service; it appears below without leaving the page.
5. Retry the same type/day/start time; see a Spanish conflict and no extra row.
6. Create `10:00–11:00` then `11:00–12:00` of the same type on the same day; both appear.
7. Open the public temple page without a session; schedules still show.

## Done when

Tests above pass and the browser pass matches the spec (form up, list down, login wall, no invented schedule data).
