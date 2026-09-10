# Data Model: Editor de servicios del templo

This feature does not add tables. It uses existing `Templo` and `Servicio` records and Django's built-in user.

## Templo

| Field | Notes |
|-------|--------|
| `id` | UUID primary key |
| `nombre` | Displayed in the editor header |
| `direccion` | Displayed in the editor header |
| `alias` | Existing; not edited on this screen |
| `imagen_url` | Existing; header already handles missing image |

**Relationships:** one templo has many servicios (`servicio_set`).

**Derived:** `get_servicios()` returns `{tipo_display: {dia_display: [hora_inicio, ...]}}`. The lower list MUST render this structure (or an empty state) without fabricating rows.

## Servicio

| Field | Notes |
|-------|--------|
| `id` | UUID primary key |
| `templo` | FK; set by the view from the URL, not by the user |
| `tipo_servicio` | Choice: Eucaristía, Confesiones, Capilla del Santísimo, Adoración Eucarística |
| `dia_de_semana` | Choice: DOM…SAB |
| `hora_inicio` | Required `TimeField` |
| `hora_fin` | Optional `TimeField` (`null`/`blank` allowed) |

**Create path:** `ServicioForm` binds `tipo_servicio`, `dia_de_semana`, `hora_inicio`, `hora_fin`. The view assigns `templo` after a valid form.

### Validation rules (form)

Compare the candidate service to **other** servicios of the **same templo**.

1. **End before start:** if `hora_fin` is set and `hora_fin < hora_inicio`, the form is invalid. Do not persist.
2. **Duplicate (FR-013):** if another servicio has the same `tipo_servicio`, `dia_de_semana`, and `hora_inicio`, the form is invalid. Do not persist.
3. **Overlap (FR-014):** only against siblings that have `hora_fin`. Intervals are half-open `[hora_inicio, hora_fin)`.
   - If the candidate has `hora_fin`: overlap when `nuevo.hora_inicio < existente.hora_fin` **and** `existente.hora_inicio < nuevo.hora_fin`.
   - If the candidate has no `hora_fin`: treat it as a point at `hora_inicio`; overlap when `existente.hora_inicio <= nuevo.hora_inicio < existente.hora_fin`.
4. **Adjacent (clarification A):** `10:00–11:00` and `11:00–12:00` (same type, same day) are **not** overlap.
5. **Different type:** same day/time is allowed.
6. **Different weekday:** same type/time is allowed.
7. **Existing without `hora_fin`:** only rule 2 applies (no interval to overlap).

Conflict messages are Spanish, attached to the form, and must not create a row.

## Editor autenticado

Django `User` (contrib.auth). Any authenticated user may open and POST the editor for any existing templo (FR-010). Anonymous users never see or persist. Parish-scoped ownership is **not** modeled in this iteration.

## State

Servicios have no workflow states. They are either persisted or rejected at create time. This feature does not update or delete existing rows.
