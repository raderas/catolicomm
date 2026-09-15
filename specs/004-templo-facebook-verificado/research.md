# Research: Enlace de Facebook y verificación del templo

## 1. Store Facebook as an optional URLField on Templo

**Decision:** Add `Templo.facebook` as `URLField(blank=True, default="", max_length=500)` with Spanish labels/errors. Include it on `TemploForm` (`fields` + `URLInput` with `form-control`). Do **not** put `verificado` on the form. On `clean_facebook`: strip whitespace; if the value has no scheme, prefix `https://`; empty stays empty. Invalid URLs fail with a Spanish message and do not persist.

**Rationale:** The spec wants a usable web address, optional, captured on the existing alta/edición screens (FR-001–FR-004). `URLField` is the idiomatic Django type (constitution I). Prefixing `https://` lets an editor paste `facebook.com/parroquia` without a cryptic error. Domain is not restricted to facebook.com: the spec does not require proving the page exists or belongs to the parish. `max_length=500` covers typical Facebook page URLs. Default `""` (no `null`) avoids two empty states.

**Alternatives considered:**
- `CharField` without URL validation — would accept “texto libre”, which FR-004 rejects.
- Require `facebook.com` host — extra false negatives (`fb.me`, `m.facebook.com`, `profile.php`) and not in the spec.
- Live HTTP check that the page exists — slow, brittle, out of spec.

## 2. Verification is a BooleanField, never on TemploForm

**Decision:** Add `Templo.verificado = BooleanField(default=False)`. Generated migration backfills existing rows as `False`. Exclude the field from `TemploForm` so a tampered POST cannot self-verify on create/edit. Add a thin model helper `revocar_verificacion()` that sets `verificado=False` and saves only when it was `True`.

**Rationale:** FR-009 / FR-012. Default false matches “todos los templos sin marcar al crear”. Keeping the flag off the ModelForm is the simplest way to guarantee editors cannot set it (constitution I, no extra permission framework).

**Alternatives considered:**
- Include a disabled checkbox on the edit form — still a mutation surface; spec says verify only on ficha/servicios header.
- Three-state null boolean — YAGNI; verified vs not is enough.

## 3. Site admin means `is_staff`; verify via a dedicated POST

**Decision:** “Administrador del sitio” is `request.user.is_staff` (the flag that grants the Django admin site). Add `POST /misas/templo/<uuid>/verificar/` (`misas:verificar_templo`):

- `@login_required`; anonymous → 302 to `/accounts/login/` with `next`.
- Non-staff authenticated → `403`; MUST NOT change `verificado`.
- POST body: CSRF, `verificado` = `"1"` or `"0"`, optional `next` (relative path to this templo’s ficha or servicios only; otherwise redirect to the ficha).
- GET → `405`.
- Unknown UUID → `404`.

Staff buttons live in `templo_header.html` so they appear on both the public ficha and the services editor without duplicating markup.

**Rationale:** Original request was “admin de django”. `is_staff` is that permission; `staff_member_required` would send people to the admin login, which is the wrong wall for this app. Explicit `"1"`/`"0"` avoids accidental toggle on double-submit. Open-redirect protection on `next` is a security default (constitution IV).

**Alternatives considered:**
- `is_superuser` only — excludes staff who can already use `/admin/` but are not superusers.
- Verify only inside Django admin changelist — spec requires the ficha and servicios screens.
- Toggle without an explicit value — double POST would flip twice.

## 4. All visitor-facing verification/Facebook UI goes in templo_header.html

**Decision:** Extend the existing shared header (already included by `templo.html` and `edit_servicios.html`):

- After the name: if not `verificado`, a small `*` immediately after `templo.nombre`; if `verificado`, a visible “Verificado” mark (e.g. check icon + text), no asterisk.
- If `templo.facebook`: `bi-facebook` + the stored address as link text, `href` = the URL, `target="_blank"` `rel="noopener noreferrer"`. If empty: render neither icon nor href.
- At the foot of the same card: always the festivities sentence; if not verified, also «La información de este templo aún está sujeta a validación.»
- Staff-only form: “Marcar como verificado” or “Quitar verificación” using existing `btn-outline-brand btn-sm` / `btn-gold` language. Hidden `next` = `request.path`.

Do **not** change listing cards (`index.html`) this iteration.

**Rationale:** FR-006–FR-010, FR-020–FR-021, and the spec’s request to reuse the block that already appears on both screens. Bootstrap Icons already load `bi-facebook` in `base.html`. Opening in a new tab matches the existing “Cómo llegar” pattern and SC “can return to the directory”. Constitution III: no new design system.

**Alternatives considered:**
- Duplicate markup on ficha vs servicios — contradicts the spec and drifts.
- Asterisk on listing cards — explicitly out of scope.
- Icon-only Facebook control — spec requires icon **and** the address.

## 5. Revoke verification on valid templo save and valid servicio create

**Decision:** After a **valid** `TemploForm` save on edit (and no-op on create, already false), call `revocar_verificacion()` on that instance before/with the save (`commit=False`, set `verificado=False` if it was true, then `save()` so photo + text + flag are one write). After a **valid** `ServicioForm` create in `templo_servicios_edit`, revoke on `templo` and re-bind the instance in context so the included header on the same `200` shows unverified.

Do **not** add service modify/delete UI. Those operations do not exist today. Document that any future persist of `Servicio` (update/delete) MUST call the same helper. Invalid form posts MUST NOT revoke (do not call the helper unless `is_valid()` and the row is saved).

**Rationale:** FR-018 / FR-019 / US5. The only current service mutation is create; wiring that path satisfies the spec without inventing editor screens (YAGNI, constitution I). Invalid saves leaving the flag alone matches the edge case.

**Alternatives considered:**
- Auto-revoke only when Facebook changes — spec says any ficha or service save.
- Skip revoke when the editor is staff — spec says the admin must re-mark; no exception.
- Build service edit/delete now so US5 “modifica o elimina” has a button — out of this feature’s FR-017 / YAGNI.

## 6. Tests and browser verification

**Decision:** Extend `misas/tests.py` (new classes next to `TemploFichaTestCase` / `ServiciosEditorTestCase`). Keep existing tests; update the create GET assertion to expect `name="facebook"`. Cover:

- Optional Facebook create/edit; empty omits icon/href on ficha **and** servicios header.
- Invalid URL (e.g. `no es una url`) → 200, Spanish error, no persist.
- Scheme-less `facebook.com/x` accepted after `https://` prefix.
- Create always `verificado=False`; extra POST `verificado=1` ignored.
- Staff POST verify `1`/`0` updates flag and header; editor 403; anonymous 302 login; GET 405.
- Valid templo edit and valid servicio create on a verified templo → `verificado=False` + asterisk + validation note.
- Invalid templo/servicio POST leaves `verificado=True`.
- Unverified header: `*` after name + validation note; verified: “Verificado”, no `*` / no validation note; both: festivities sentence.

Browser pass: create with Facebook, public click-out, staff mark, editor edit revokes, add service revokes, notes visible signed-out.

**Rationale:** Constitution II: temple detail, create/edit, and service schedules are critical paths. Browser supplements tests; it does not replace them.

**Alternatives considered:**
- Browser-only — not allowed as sole evidence.
- pytest-django — project uses `manage.py test`.
