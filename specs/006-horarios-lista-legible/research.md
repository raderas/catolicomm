# Research: Horarios de servicios como lista legible

## 1. Stop dumping the Python list; join in the template

**Decision:** On `misas/templates/misas/templo.html`, replace `{{ horas }}` with a comma-space join of the list (`{{ horas|join:", " }}` or equivalent). Keep the same join on `misas/templates/misas/edit_servicios.html` (already present). Do not iterate into a new visual layout.

**Rationale:** Django’s default string for a `list` is Python `repr` (`['08:00', '10:00']`), which is the defect in FR-001/FR-003. `join` is the built-in way to render a list as readable text. The editor already does this; the ficha must match (US2 scenario 3). Constitution I: no new component, just the filter already used next door.

**Alternatives considered:**
- `{{ horas }}` plus CSS — still shows brackets and quotes.
- JSON serialize — still not a Spanish list.
- One `<span>` per hour — extra markup; spec asks for a comma-separated list, not chips.

## 2. Convert to 12-hour Spanish only at display; keep `TimeField`

**Decision:** Do **not** migrate `Servicio.hora_inicio` (or `hora_fin`). Keep storing `datetime.time`. Format each start time when building the derived list in `Templo.get_servicios()` (or a tiny helper it calls). The alta form keeps posting `HH:MM` via the existing `TimeInput`.

**Rationale:** Spec FR-008/FR-009 and clarification 2026-09-15: convert in the consult UI; storage unchanged. `get_servicios()` already turns `hora_inicio` into display strings (`strftime("%H:%M")`); swapping that conversion to 12-hour Spanish keeps one source of truth for both screens and leaves the column type alone (constitution I, V, YAGNI).

**Alternatives considered:**
- Store `"8:00 a. m."` as `CharField` — changes the model, breaks overlap math, contradicts FR-009.
- Format only in templates with `|time:"g:i a"` — Django’s `a` is typically `a.m.` without spaces, often locale-English; spec requires `a. m.` / `p. m.` and no leading zero. Fighting `FORMAT_MODULE` is more moving parts than a 10-line helper.
- JavaScript `toLocaleTimeString` — constitution and YAGNI: schedule text must come from `Servicio`, not a client rewrite that can disagree with tests.

## 3. Exact 12-hour mapping

**Decision:** Helper maps `datetime.time` → `f"{h12}:{mm:02d} {suffix}"` where:

| Stored hour | Display |
|-------------|---------|
| 00:MM | `12:MM a. m.` |
| 01:MM–11:MM | `{h}:{MM} a. m.` (no leading zero) |
| 12:MM | `12:MM p. m.` |
| 13:MM–23:MM | `{h-12}:{MM} p. m.` |

Minutes always two digits. Suffix is exactly `a. m.` or `p. m.` (spaces after the periods). Do not emit `AM`, `PM`, `a.m.`, or `H:i` 24-hour.

**Rationale:** Spec edge cases and FR-008. Explicit mapping is testable and does not depend on OS locale (constitution II).

**Alternatives considered:**
- Babel / `dateformat` with custom format — extra dependency for one string.
- Leading-zero `08:00 a. m.` — rejected in clarify (option D).

## 4. Order, grouping, and empty state stay as today

**Decision:** `get_servicios()` keeps `{tipo_display: {dia_display: [hora, ...]}}`. Append order stays the current loop over `servicio_set` (no new sort). Empty `{}` still drives the editor empty copy; the ficha keeps its current empty-tabs behavior. `hora_fin` is still not shown in these lists. `get_proxima_misa` on `index.html` is out of scope.

**Rationale:** FR-005/FR-006 and spec assumptions. Changing sort or showing end times would be a second product change.

**Alternatives considered:**
- Sort hours ascending — nicer, but not requested; risks a visible reorder vs today’s list.
- Include `hora_fin` as ranges — out of spec.

## 5. Tests must follow the display string; POST stays 24-hour

**Decision:** Add/adjust `Client` tests in `misas/tests.py` so GET `misas:templo` and GET `misas:templo_servicios` assert `8:00 a. m.` (and comma-separated multiples), and MUST NOT contain `[`, `'` around hours, `18:00`, or `AM`/`PM`. Keep creating servicios with `time(10, 0)` / POST `"10:00"`. Reload the instance and assert `hora_inicio` is still `time(...)`.

**Rationale:** Constitution II (temple detail + service schedules). Existing US2 list tests that `assertContains(..., "10:00")` / `"18:00"` will need the 12-hour strings or they will pass for the wrong reason (`10:00` is a substring of `10:00 a. m.` — prefer asserting the full display token and a 24-hour absence).

**Alternatives considered:**
- Browser-only — not allowed as sole critical-path evidence.
- Snapshot the Python `repr` — that is the bug.
