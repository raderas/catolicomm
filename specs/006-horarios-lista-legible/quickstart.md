# Quickstart: Horarios de servicios como lista legible

Validate this feature after implementation. Display mapping is in [data-model.md](./data-model.md); HTML rules are in [contracts/horarios-legibles.md](./contracts/horarios-legibles.md).

## Prerequisites

- Python 3.12, project virtualenv, dependencies from `requirements.txt`
- Env vars already used by the app (`DJANGO_SECRET_KEY`, database settings)
- At least one Django user and one `Templo` with several `Servicio` rows on the same weekday (include a morning time and an afternoon time, e.g. 08:00 and 18:00)

## Automated checks

From the repo root:

```bash
python manage.py test misas
```

Expect coverage of:

- Anonymous GET `misas:templo` shows `8:00 a. m., 10:00 a. m., 6:00 p. m.` (or the hours present), not `['08:00'` / `'18:00']` / `18:00` in the schedule list
- Authenticated GET `misas:templo_servicios` lower list uses the same strings
- Single hour → `8:00 a. m.` with no trailing comma
- `00:00` → `12:00 a. m.`; `12:00` → `12:00 p. m.`
- After GET, `Servicio.hora_inicio` is still the stored `time`
- Existing create/overlap POSTs still accept `"10:00"` and persist `time(10, 0)`
- Existing temple/service/navbar tests stay green

## Manual browser pass (required for UI)

1. Open the public ficha of a templo with several hours the same day. Confirm the day row reads as a comma-separated list (`8:00 a. m., …`), with `a. m.` / `p. m.` and no brackets or quotes.
2. Confirm an afternoon mass shows as `6:00 p. m.` (not `18:00`).
3. Sign in and open Agregar servicio for the same templo. Confirm the lower list matches the ficha.
4. Confirm the create form still uses the existing time fields (no change to how a new hour is typed).
5. Reload the ficha; hours did not shift and no extra servicio appeared.

## Done when

Tests above pass and the browser pass matches the spec (readable 12-hour lists on ficha and editor, storage unchanged).
