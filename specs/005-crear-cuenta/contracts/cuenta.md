# Contract: Crear cuenta, confirmación y restablecimiento

Internal Django HTML + mail contract. Not a public JSON API.

State and field rules: [data-model.md](../data-model.md).

## Login screen (`GET /accounts/login/`, name `login`)

Anonymous `200`. Existing Spanish card **plus**:

| Control | Points at |
|---------|-----------|
| **Crear cuenta** | `{% url 'crear_cuenta' %}` (`/accounts/crear-cuenta/`) |
| **Olvidé mi contraseña** | `{% url 'password_reset' %}` (`/accounts/password_reset/`) |

MUST NOT use English **Sign up** / **Register** / **Forgot password**. MUST NOT add those links to `base.html`.

| Session | GET login | POST login |
|---------|-----------|------------|
| Anonymous, active user, valid password | form | `302` to `next` or `/misas/perfil/` (unchanged) |
| Anonymous, **pending** user, correct password | form | **not** authenticated; Spanish inactive error + resend path |
| Anonymous, wrong password | form | existing failure (do not say “unconfirmed”) |
| Authenticated | `302` away (`redirect_authenticated_user`) | n/a |

## Routes

| Method | Path | Name | Auth | Result |
|--------|------|------|------|--------|
| GET | `/accounts/crear-cuenta/` | `crear_cuenta` | Anonymous | `200`. Spanish alta: Usuario, Correo de contacto, Contraseña, Confirmación. Link back to `login`. Same card language as login. |
| GET | `/accounts/crear-cuenta/` | `crear_cuenta` | Authenticated | `302` to `/misas/perfil/` (or safe `next`). MUST NOT show the guest form. |
| POST | `/accounts/crear-cuenta/` | `crear_cuenta` | Anonymous | CSRF. Invalid → `200` with Spanish errors; username/email preserved; passwords empty; **no** `User` row; **no** mail. Valid → create `User` (`is_active=False`, not staff); **one** confirmation email to `User.email`; session still anonymous; `302` to `cuenta_creada`. |
| GET | `/accounts/cuenta-creada/` | `cuenta_creada` | Anonymous | `200`. Spanish “revisa tu correo”; resend path; link to login. MUST NOT start a session. |
| GET | `/accounts/confirmar/<uidb64>/<token>/` | `confirmar_correo` | any | See confirmation table below. |
| GET/POST | `/accounts/reenviar-confirmacion/` | `reenviar_confirmacion` | Anonymous | GET `200` username form. POST CSRF: always generic success. Mail only if pending user with email. Authenticated → `302` to perfil. |
| GET/POST | `/accounts/password_reset/` | `password_reset` | Anonymous | GET `200` **Usuario** (not email). POST CSRF: always `302`/`200` done with generic copy. Mail only if **active** user with email. Authenticated → `302` to perfil. |
| GET | `/accounts/password_reset/done/` | `password_reset_done` | Anonymous | `200`. Generic Spanish “si la cuenta existe, enviamos un correo”. |
| GET/POST | `/accounts/reset/<uidb64>/<token>/` | `password_reset_confirm` | Anonymous | Invalid/expired token → Spanish failure, password unchanged. Valid GET → new password + confirmation. Valid POST → set password; old password fails login; `302` to complete. |
| GET | `/accounts/reset/done/` | `password_reset_complete` | Anonymous | `200`. Spanish; link to **Iniciar sesión**. MUST NOT auto-login. |

`LOGIN_URL` stays `/accounts/login/`. `LOGIN_REDIRECT_URL` stays `/misas/perfil/`.

## Signup POST body

| Field | Required | Notes |
|-------|----------|--------|
| `csrfmiddlewaretoken` | yes | |
| `username` | yes | Unique; charset of `User.username` |
| `email` | yes | Valid email; not unique |
| `password1` | yes | Validators |
| `password2` | yes | Must match `password1` |

## Confirmation GET

| Situation | Result |
|-----------|--------|
| Valid token, pending user | `is_active=True`; `login()`; `302` to `/misas/perfil/`; user sees own email/username; **no** password in HTML |
| Already active user (old link after confirm) | Do not deactivate. Spanish “ya confirmada” and path to login or perfil. Token MUST NOT reset a password. |
| Bad uid, bad/expired/reused token | `200` invalid page in Spanish; account stays pending if it was pending; offer resend |
| Pending user, valid token used a second time | Invalid; still active from the first use; no double session requirement |

## Mail

| Trigger | Recipients | MUST include | MUST NOT include |
|---------|------------|--------------|------------------|
| Valid signup or valid resend | that user’s `email` | Spanish subject/body; absolute confirm URL (`confirmar_correo`) | password, other users’ data |
| Valid reset (active + email) | that user’s `email` | Spanish subject/body; absolute reset-confirm URL | password, whether other usernames exist |

Zero messages when validation fails, username unknown, pending user requests **reset**, active user requests **resend**, or email is empty.

From-address: `DEFAULT_FROM_EMAIL` (env). Tests: locmem `outbox` length and link extract.

## Isolation / security

| Situation | Result |
|-----------|--------|
| Pending credentials vs `login_required` editor | `302` to login; **no** `Servicio`/`Templo` insert |
| `Client.login` pending user | `False`; no session |
| Resend/reset response body | MUST NOT differ between unknown / pending / active / no-email in a way that reveals the case |
| Confirmation token on password-reset confirm URL | MUST NOT change the password |
| Reset token on `confirmar_correo` | MUST NOT activate |
| Two accounts sharing one email | Each has its own username and its own links |

## Out of scope (MUST NOT appear)

Custom user model, `email_verified` column, unique email constraint, navbar **Crear cuenta**, password change on Mi perfil, profile name fields on signup, staff flags granted at signup, JSON API, social login.
