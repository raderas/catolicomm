# Contract: Lista legible de horarios

Internal Django HTML contract. Not a public JSON API.

Display mapping: [data-model.md](../data-model.md). Create/POST of servicios stays [edit-servicios.md](../../001-servicios-editor-ui/contracts/edit-servicios.md) (`hora_inicio` still a time field).

## Routes (display deltas)

| Method | Path | Name | Auth | Result |
|--------|------|------|------|--------|
| GET | `/misas/templo/<uuid:id_templo>/` | `misas:templo` | Public | `200`. For each tipo/día, hours appear as a comma-separated 12-hour Spanish list. Body MUST NOT contain Python list `repr` (`[`, `'` wrapping hours) or 24-hour tokens for those rows (`18:00` when the stored time is 18:00). Unknown UUID → `404`. |
| GET | `/misas/templo/<uuid:id_templo>/servicios/` | `misas:templo_servicios` | Authenticated | `200`. Lower list uses the **same** hour strings and join as the ficha. Create form `hora_inicio` / `hora_fin` widgets unchanged. Anonymous → existing login `302`. |
| GET | `/misas/` | `misas:index` | Public | Unchanged for this feature (próxima misa out of scope). |

No new routes. No new POST fields.

## Visible hour list (both GETs above)

Given stored start times `08:00`, `10:00`, `18:00` on the same tipo and day, the HTML for that row MUST contain:

```text
8:00 a. m., 10:00 a. m., 6:00 p. m.
```

MUST NOT contain:

```text
['08:00', '10:00', '18:00']
08:00
18:00
8:00 AM
8:00 a.m.
```

Single stored `08:00` → `8:00 a. m.` with no trailing comma.

Stored `00:00` → `12:00 a. m.`. Stored `12:00` → `12:00 p. m.`.

## Storage after GET

GET MUST NOT update `Servicio.hora_inicio`. After viewing the ficha, the column is still the original `time`.

## Auth (unchanged)

| Screen | Anonymous |
|--------|-----------|
| Ficha `misas:templo` | `200` with the readable list |
| Editor `misas:templo_servicios` | `302` to `/accounts/login/` with `next` |
