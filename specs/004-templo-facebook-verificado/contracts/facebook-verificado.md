# Contract: Facebook y verificación del templo

Internal Django HTML contract. Not a public JSON API.

Field rules: [data-model.md](../data-model.md). Existing create/edit auth and photo contract in `specs/002-templo-foto-edicion/contracts/templo-ficha.md` remains; this file adds Facebook, header display, verify POST, and revoke.

## Routes (additions / deltas)

| Method | Path | Name | Auth | Result |
|--------|------|------|------|--------|
| GET | `/misas/templo/nuevo/` | `misas:nuevo_templo` | Authenticated | `200`. Spanish create form includes `facebook` (optional) in addition to nombre, dirección, alias, imagen. MUST NOT include a control that sets `verificado`. |
| POST | `/misas/templo/nuevo/` | `misas:nuevo_templo` | Authenticated | CSRF. Valid → insert with `verificado=False` (ignore client `verificado`) and optional `facebook`; `302` to ficha. Invalid Facebook URL → `200`, Spanish error, no row. |
| GET | `/misas/templo/<uuid:id_templo>/editar/` | `misas:editar_templo` | Authenticated | `200`. Form includes current `facebook`. No verify checkbox. |
| POST | `/misas/templo/<uuid:id_templo>/editar/` | `misas:editar_templo` | Authenticated | CSRF. Valid → update ficha fields; if `verificado` was true, persist `False`. `302` to ficha. Invalid → `200`, no field changes, `verificado` unchanged. |
| POST | `/misas/templo/<uuid:id_templo>/servicios/` | `misas:templo_servicios` | Authenticated | Unchanged create contract, plus: valid insert → if templo was verified, persist `verificado=False` and the `200` header MUST show unverified (asterisk + validation note). Invalid → no servicio, flag unchanged. |
| POST | `/misas/templo/<uuid:id_templo>/verificar/` | `misas:verificar_templo` | Anonymous | `302` to login with `next`. MUST NOT change `verificado`. |
| POST | `/misas/templo/<uuid:id_templo>/verificar/` | `misas:verificar_templo` | Authenticated, not staff | `403`. MUST NOT change `verificado`. |
| POST | `/misas/templo/<uuid:id_templo>/verificar/` | `misas:verificar_templo` | Staff | CSRF required. `verificado=1` → True; `verificado=0` → False. `302` to `next` if it is a relative path for this templo’s ficha or servicios; otherwise `302` to ficha. Unknown UUID → `404`. |
| GET | `/misas/templo/<uuid:id_templo>/verificar/` | `misas:verificar_templo` | Any | `405`. |

Login uses existing `/accounts/login/`. CSRF middleware stays on.

## POST body — templo create/edit (delta)

| Field | Required | Notes |
|-------|----------|-------|
| `facebook` | no | URL. Empty allowed. Whitespace stripped; missing scheme → `https://`. |
| `verificado` | n/a | MUST be ignored if present. |

Photo/text fields unchanged from 002.

## POST body — verificar

| Field | Required | Notes |
|-------|----------|-------|
| `csrfmiddlewaretoken` | yes | |
| `verificado` | yes | `"1"` or `"0"`. |
| `next` | no | Relative path only; must target this templo’s `misas:templo` or `misas:templo_servicios`. |

## Validation outcomes (Facebook)

| Situation | Persist? | User-visible |
|-----------|----------|--------------|
| Valid create with Facebook URL | yes | Redirect to ficha; header shows icon + address |
| Valid create without Facebook | yes | Ficha has no Facebook icon or href |
| Valid edit changing only Facebook | yes | New/empty Facebook on ficha; other ficha fields unchanged; verified templo becomes unverified |
| Invalid URL | no | Spanish field error |
| Client POST `verificado=1` on create/edit | insert/update ficha only | Row stays/becomes `verificado=False` |

## Shared header (`templo_header.html`) on ficha and servicios

Public ficha (`GET misas:templo`) remains unauthenticated. Servicios editor remains login-required. Both include the same header.

| State | MUST show | MUST NOT show |
|-------|-----------|----------------|
| `facebook` set | `bi-facebook`, the URL text, followable `href` (`target="_blank"`, `rel="noopener noreferrer"`) | empty icon / empty href |
| `facebook` empty | — | Facebook icon or address |
| `verificado=False` | `*` immediately after the name; note «La información de este templo aún está sujeta a validación.» | “Verificado” mark |
| `verificado=True` | “Verificado” mark | asterisk; pending-validation note |
| any | «La información y horarios pueden estar sujetos a modificaciones o excepciones en fechas especiales/festividades.» | |
| `user.is_staff` | POST form to `misas:verificar_templo` (Marcar / Quitar) | |
| not staff (including anonymous on ficha) | — | verify form / buttons |

Listing (`misas:index`) is unchanged: no Facebook, asterisk, notes, or Verificado required.

## Verify-only POST MUST NOT

Create, update, or delete `Servicio` rows, or change nombre, dirección, alias, imagen, or facebook.
