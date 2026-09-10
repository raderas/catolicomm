# Contract: Editor de servicios (`misas:templo_servicios`)

Internal Django HTML contract. Not a public JSON API.

## Routes

| Method | Path | Auth | Result |
|--------|------|------|--------|
| GET | `/misas/templo/<uuid:id_templo>/servicios/` | Anonymous | `302` to login with `next` pointing at this URL. Body MUST NOT include the create form or the editor list. |
| GET | `/misas/templo/<uuid:id_templo>/servicios/` | Authenticated | `200`. Temple header, create form (upper), existing services (lower) or empty copy. Unknown UUID → `404`. |
| POST | `/misas/templo/<uuid:id_templo>/servicios/` | Anonymous | `302` to login. MUST NOT insert a `Servicio`. |
| POST | `/misas/templo/<uuid:id_templo>/servicios/` | Authenticated | CSRF required. Valid → persist one `Servicio` for that templo and `200` with the new row in the lower list. Invalid (including duplicate/overlap) → `200` with Spanish form errors, no new row. |
| GET | `/accounts/login/` | Anonymous | `200`. Spanish sign-in form, same visual language as the directory. |

Name: `misas:templo_servicios`. Login uses Django auth `login`.

## POST body (form)

| Field | Required | Notes |
|-------|----------|--------|
| `csrfmiddlewaretoken` | yes | Existing CSRF middleware stays on. |
| `tipo_servicio` | yes | Value from `Servicio.TipoServicio`. |
| `dia_de_semana` | yes | Value from `Servicio.DiasSemana`. |
| `hora_inicio` | yes | Time. |
| `hora_fin` | no | Time; if present must not be earlier than `hora_inicio`. |

`templo` is not accepted from the client; it comes from the URL.

## Validation outcomes

| Situation | Persist? | User-visible |
|-----------|----------|--------------|
| Valid, no conflict | yes | New service appears in the lower list |
| Duplicate same type, day, `hora_inicio` | no | Spanish conflict on the form |
| Overlap with same type that has `hora_fin` (interior intersection) | no | Spanish conflict on the form |
| Adjacent half-open intervals | yes | Both services listed |
| Other type, same slot | yes | Both services listed |
| `hora_fin` before `hora_inicio` | no | Spanish field/form error |
| Empty templo (no services) | n/a (GET) | Empty-state copy in Spanish, not a blank lower card |

## Public pages (unchanged access)

| Route | Auth |
|-------|------|
| `misas:index` | Public |
| `misas:templo` | Public. “Agregar servicio” may remain; following it as anonymous hits the login contract above. |
