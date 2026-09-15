# Data Model: Enlace de Facebook y verificación del templo

This feature adds two fields on `Templo`. It does not add tables. Django’s built-in user remains the editor identity; `is_staff` is the verifier.

## Templo

| Field | Type | Rules |
|-------|------|--------|
| `id` | UUID PK | Unchanged |
| `nombre` | char, max 100 | Required on create and edit |
| `direccion` | char, max 1000 | Required on create and edit |
| `alias` | char, max 100 | Optional; empty string allowed |
| `imagen` | optional image file | Unchanged |
| `facebook` | URL, max 500 | Optional; `blank=True`, `default=""`; empty means “no Facebook” |
| `verificado` | boolean | Default `False`; not on `TemploForm`; only staff POST may set `True` |

**Relationships:** one templo has many servicios (`servicio_set`). Unchanged. This feature MUST NOT add service update/delete screens. A successful **create** of `Servicio` MUST revoke `verificado` when it was `True`.

**Derived display (shared header only):**

- Facebook: if `facebook` is non-empty, show icon + address as a followable link; otherwise show nothing.
- If `verificado` is true: show “Verificado”; no asterisk; no pending-validation note.
- If `verificado` is false: asterisk immediately after `nombre`; pending-validation note at the foot of the header.
- Always: festivities note at the foot of the header.

Listing cards do not use these fields in this iteration.

## Facebook validation (form)

1. Empty / omitted → valid; stored as `""`.
2. Leading/trailing whitespace stripped.
3. If non-empty and no `http://` or `https://` scheme, prefix `https://`.
4. After that, MUST be a usable HTTP(S) URL. Other strings are invalid (Spanish error); create does not insert; edit does not change the row (including `verificado`).
5. The host NEED NOT be `facebook.com`. Existence of the remote page is not checked.

## Verification state

```text
                    create / existing rows
                              │
                              ▼
                      ┌───────────────┐
          staff POST  │ no verificado │  valid ficha save
          verificado=1│               │◄──── or valid servicio create
                ┌────►│               │
                │     └───────┬───────┘
                │             │ staff POST verificado=1
                │             ▼
                │     ┌───────────────┐
                └─────│  verificado   │
    staff POST        └───────────────┘
    verificado=0
    or valid ficha/servicio save
```

1. **Create:** always `False`, even if the client POSTs `verificado`.
2. **Existing rows:** migration default `False`.
3. **Staff mark:** POST `verificado=1` → `True`. POST `verificado=0` → `False`.
4. **Revoke:** valid templo edit save or valid servicio insert → `False` if it was `True`. Staff who edit must re-mark.
5. **Invalid save:** flag unchanged.
6. **Verify-only POST:** MUST NOT change nombre, dirección, alias, foto, facebook, or servicios.

Helper: `Templo.revocar_verificacion()` — if `verificado`, set false and persist (or set on `commit=False` instance before the ficha save).

## Editor autenticado

Django `User`. Any authenticated user may create/edit ficha (including `facebook`) and create servicios, as in 001/002. They MUST NOT change `verificado` via those forms or via the verify route.

## Administrador del sitio

`User.is_staff is True`. May POST the verify route. If they save ficha or create a servicio, revocation still applies.

## Media / other fields

Photo rules from 002 are unchanged. `facebook` is text, not a file.
