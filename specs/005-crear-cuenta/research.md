# Research: Crear cuenta, verificar correo y recuperar contraseña

## 1. Confirmation state is `User.is_active`, not a new field

**Decision:** On a valid signup, `UserCreationForm.save()` creates a contrib.auth `User` with `username`, `email`, hashed password, `is_staff=False`, `is_superuser=False`, and **`is_active=False`**. Do not call `login()`. Do not add `email_verified`, a profile table, or a custom user model. Admin/`createsuperuser` users stay `is_active=True` and keep signing in without this email step.

**Rationale:** Spec FR-013/FR-014/FR-022/FR-025: the account exists but cannot authenticate until the contact email is confirmed; preexisting accounts are not blocked. Django’s `ModelBackend` already refuses inactive users, and `login_required` editors therefore stay closed. Constitution I / YAGNI: `is_active` is the built-in “may log in” flag.

**Alternatives considered:**
- `BooleanField` `email_verified` on a profile / custom user — extra migration and a second source of truth next to `is_active`.
- Create active and restrict editors in each view — easy to miss a `login_required` route; inactive-at-source is smaller.
- django-allauth — new identity stack; forbidden by constitution I and YAGNI.

## 2. Signup is `UserCreationForm` + email, not a hand-rolled user writer

**Decision:** Add `CrearCuentaForm(UserCreationForm)` with a required `EmailField` (label **Correo de contacto**). Keep Django’s username validators and `AUTH_PASSWORD_VALIDATORS` (min 8, similarity, common, numeric) plus `password1`/`password2`. `save()` sets `email` and `is_active=False`. View: thin `CreateView`/`FormView` that, on success, sends the confirmation mail and redirects to a **Revisa tu correo** page without a session. Authenticated GET/POST of signup redirects to `LOGIN_REDIRECT_URL` (Mi perfil), same idea as `LoginView.redirect_authenticated_user`.

**Rationale:** Spec FR-004–FR-012. `UserCreationForm` is the project-appropriate reuse of contrib.auth (constitution I). Email is stored on `User.email` (already shown on Mi perfil). Username uniqueness is already the model constraint.

**Alternatives considered:**
- `ModelForm` on `User` with a raw password field — would skip validators unless reimplemented.
- Sign the person in after signup — contradicts FR-013.
- Unique email constraint — spec allows shared parish inboxes; uniqueness stays on `username`.

## 3. Confirmation tokens: salted `PasswordResetTokenGenerator`, not the reset generator

**Decision:** `misas/tokens.py` defines `EmailConfirmationTokenGenerator(PasswordResetTokenGenerator)` with a distinct `key_salt` (e.g. `"misas.email_confirmation"`). Links: `/accounts/confirmar/<uidb64>/<token>/`. GET handler: resolve uid; if user missing → invalid page; if already `is_active` → send them to login or perfil with a Spanish “ya está confirmada” outcome (do not error as if the account were unknown); if inactive and token valid → `is_active=True`, `login(..., backend=ModelBackend)`, redirect to `/misas/perfil/`; if token invalid/expired → `confirmacion_invalida` + resend path. Expiry uses existing `PASSWORD_RESET_TIMEOUT` (default three days).

**Rationale:** Spec FR-023 (one-time, expiring, then session). Django’s generator already hashes `pk`, password, `last_login`, `is_active`, and email — flipping `is_active` to `True` invalidates the confirmation token. A **different `key_salt`** prevents a confirmation token from being accepted by `PasswordResetConfirmView` and vice versa.

**Alternatives considered:**
- Reuse `default_token_generator` for both flows — a leaked confirmation URL could be posted to the reset-confirm route.
- `TimestampSigner` only — works, but we would reimplement expiry/user binding that the auth generator already has.
- POST-only confirm — email clients issue GET; Django password reset confirm also starts with GET.

## 4. Mail: console locally, locmem in tests, From-address from env

**Decision:** Keep `MAILERS["default"]` as `console.EmailBackend` for development. In the existing `if "test" in sys.argv` block, switch that backend to `django.core.mail.backends.locmem.EmailBackend` and assert on `django.core.mail.outbox`. Set `DEFAULT_FROM_EMAIL` from the environment (fallback only for empty local/dev, never a secret). Confirmation and reset bodies/subjects are Spanish templates under `misas/templates/registration/`. No password in any message.

**Rationale:** Spec assumption: the visitor always sees “revisa tu correo”; real SMTP is an ops prerequisite. Constitution IV: secrets/config in env. Tests must not depend on an inbox.

**Alternatives considered:**
- Always SMTP in development — extra account, slower tests.
- Third-party ESP SDK — YAGNI for this traffic.

## 5. Inactive login message + resend, without leaking existence

**Decision:** Point `LoginView` at `AutenticacionForm(AuthenticationForm)` with a Spanish `inactive` error: the account is not confirmed yet. Login template also links **Reenviar correo de confirmación**. Resend is a small form (**Usuario** only) that always shows the same generic success copy. Mail is sent only if that username exists, `is_active=False`, and `email` is non-empty; a new token invalidates the previous one because it is a new hash at a new timestamp (old tokens expire; do not keep a stored nonce). Authenticated users hitting resend/signup/reset are redirected away from the guest forms.

**Rationale:** FR-014, FR-024, FR-017, SC-011. Django already raises on inactive; we only replace the English/generic wording and add the resend path.

**Alternatives considered:**
- Reveal “that username is not pending” — username enumeration; forbidden by SC-011.
- Resend by email address — ambiguous with shared inboxes; username is the identifier.

## 6. Password reset reuses contrib.auth views, keyed by username

**Decision:** `django.contrib.auth.urls` already mounts reset views under `/accounts/`. Register `PasswordResetView` **before** that include (same pattern as `LoginView`) with `form_class=UsernamePasswordResetForm`. The form has `username` (not `email`). `save()` looks up `User`; sends the stock reset email **only** when `is_active=True` and `email` is non-empty; always returns the `password_reset_done` page with generic copy. `PasswordResetConfirmView` / complete stay the framework views, with Spanish templates in the same cream/gold card. New password uses the same validators + confirmation. After a successful reset the person **logs in** (no auto-login). Inactive / missing / emailless users get the generic done page and no useful mail.

**Rationale:** FR-026–FR-028. Email is not unique, so Django’s default “enter your email” form would either spam every matching account or be ambiguous. Username is the login identifier. Reusing `PasswordResetView` keeps CSRF, token expiry, and one-time invalidation (password change updates the hash) without a new token stack.

**Alternatives considered:**
- Reset by email (Django default) — conflicts with shared parish mailboxes.
- Custom reset views from scratch — duplicates contrib.auth.
- Auto-login after reset — not required by FR-027; login is the existing session path.
- Password change from Mi perfil — explicitly out of spec this iteration.

## 7. Login screen gains both guest actions; URLs stay under `/accounts/`

**Decision:** On `registration/login.html`, below the submit button, add **Crear cuenta** → `crear_cuenta` and **Olvidé mi contraseña** → `password_reset`. Do not put those links in `base.html`. Routes:

| Path | Name |
|------|------|
| `/accounts/crear-cuenta/` | `crear_cuenta` |
| `/accounts/cuenta-creada/` | `cuenta_creada` |
| `/accounts/confirmar/<uidb64>/<token>/` | `confirmar_correo` |
| `/accounts/reenviar-confirmacion/` | `reenviar_confirmacion` |
| `/accounts/password_reset/` | `password_reset` (override) |
| existing `password_reset_done` / `password_reset_confirm` / `password_reset_complete` | unchanged names |

**Rationale:** Spec: both actions live on the login screen, not the navbar. Identity already lives at `/accounts/login/`; keep that prefix. Spanish path segments for the new screens; keep Django’s reset path names so `auth.urls` still wires confirm/complete.

**Alternatives considered:**
- `/misas/crear-cuenta/` — splits identity across apps for no gain.
- Navbar **Crear cuenta** — out of spec.

## 8. Tests and browser verification

**Decision:** New `TestCase` classes in `misas/tests.py` (do not weaken temple/service or navbar/perfil classes). Use `Client.login()` (not `force_login`) when asserting that inactive users cannot authenticate — `force_login` bypasses `is_active`. Cover: login HTML has both links; valid signup creates inactive user + one outbox message + no session; validation errors send no mail; confirm GET activates, logs in, lands on perfil; second use of the same link fails; inactive login fails with Spanish copy; resend generic; reset by username for active+email; inactive reset sends no mail; new password works, old does not; existing `create_user` editors still reach servicios. Locmem mail in tests. Browser pass: desktop + collapsed login, signup, (console/outbox) confirm, reset.

**Rationale:** Constitution II: login wall is how editors reach schedule mutation. Browser supplements; it does not replace `manage.py test`.

**Alternatives considered:**
- Browser-only — not allowed as sole evidence.
- pytest / mail mock library — extra runner; locmem is enough.
