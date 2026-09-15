# Data Model: Horarios de servicios como lista legible

This feature does **not** add tables or fields. It only changes how stored start times are **read** on two screens.

## Servicio (unchanged storage)

| Field | Notes |
|-------|--------|
| `id` | UUID primary key |
| `templo` | FK |
| `tipo_servicio` | Choice (display name used as grouping key) |
| `dia_de_semana` | Choice (display name used as grouping key) |
| `hora_inicio` | Required `TimeField` — **stored value must not change** |
| `hora_fin` | Optional `TimeField` — not shown in these day lists |

**Create/edit:** `ServicioForm` still binds `hora_inicio` / `hora_fin` as times. No new validators for this feature.

## Templo (unchanged)

Public ficha and editor header already load one `Templo`. Schedule rows come from `servicio_set`.

## Derived: lista de horas del día

`Templo.get_servicios()` remains:

```text
{ tipo_display: { dia_display: [hora_display, ...] } }
```

Each `hora_display` is the **display** of that row’s `hora_inicio`, not a new column:

| Stored `hora_inicio` | `hora_display` |
|----------------------|----------------|
| `00:00` | `12:00 a. m.` |
| `08:00` | `8:00 a. m.` |
| `10:00` | `10:00 a. m.` |
| `12:00` | `12:00 p. m.` |
| `18:00` | `6:00 p. m.` |

**Join rule (UI):** hours for one day render as `hora_display` values separated by `", "` (comma + space). One hour → that string alone (no trailing comma).

**Integrity:**

1. Count of `hora_display` for a tipo+día MUST equal the count of `Servicio` rows for that templo, tipo, and weekday.
2. Order MUST match the current `get_servicios()` append order (iteration of `servicio_set`).
3. Formatting MUST NOT write back to `hora_inicio`.
4. Empty `get_servicios()` → no fabricated hours (existing empty copy on the editor).

## State

No workflow. A `Servicio` is stored or not; this feature never updates the time column as a side effect of GET.
