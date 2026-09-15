# Data Model: Crear cuenta, verificar correo y recuperar contraseña

This feature does **not** add tables or migrate `Templo` / `Servicio`. Identity stays Django’s built-in `User` (`django.contrib.auth`). Confirmation is `is_active`. Tokens are not stored as rows.

## User (cuenta)

| Attribute | Signup | After confirm | Notes |
|-----------|--------|---------------|--------|
| `username` | required, unique | unchanged | Login identifier. Letters, digits, `@ . + - _`; max length = model default (150). Label: **Usuario**. |
| `email` | required, valid format, **not unique** | unchanged | Contact + mail channel. Label: **Correo de contacto**. Not used to sign in. |
| `password` | required; validators + confirmation | same hash until reset | Never displayed or emailed. |
| `is_active` | **`False`** | **`True`** | Gate for `ModelBackend` and therefore for perfil / temple editors. |
| `is_staff` / `is_superuser` | `False` | `False` | MUST NOT be granted by this path. |
| `first_name` / `last_name` | left empty | empty | Mi perfil already shows **No registrado**. |
| `date_joined` | set by Django | unchanged | Visible on Mi perfil after confirm. |

Preexisting / admin-created users: `is_active=True` (unless an admin deactivated them). This feature MUST NOT bulk-deactivate them.

**Relationships:** none new. MUST NOT write `Templo` or `Servicio` during signup/confirm/reset.

## Account states

```text
[visitor]
    │ valid signup POST
    ▼
[pending]  is_active=False, no session, confirmation mail sent
    │ valid confirm GET
    ▼
[confirmed]  is_active=True, session started → Mi perfil
    │ logout / later login
    ▼
[confirmed, session or not]
```

| State | Sign in | Mi perfil / editar horarios | Password reset mail | Confirm mail |
|-------|---------|-----------------------------|---------------------|--------------|
| Pending | no (Spanish inactive + resend) | no | no (generic page only) | yes (signup + resend) |
| Confirmed | yes | yes (same as today’s collaborator) | yes if `email` non-empty | no |
| Preexisting active | yes | yes | yes if `email` non-empty | not required |
| Missing / unknown username | login fails as today | n/a | generic page, no mail | generic resend page, no mail |

Invalid, expired, or reused confirmation/reset links do not change state.

## Tokens (not persisted)

| Kind | Binding | Invalid when |
|------|---------|----------------|
| Email confirmation | uid + `EmailConfirmationTokenGenerator` (`key_salt` distinct from password reset) | Expiry (`PASSWORD_RESET_TIMEOUT`), `is_active` becomes True, password/email change, or newer timestamped token takes over in practice via expiry/use-once at the view |
| Password reset | uid + `default_token_generator` | Expiry, successful password change (hash in token), user inactive |

Views MUST check the matching generator so a confirmation URL cannot reset a password.

## Session

Django session authentication already in middleware.

| Event | Session |
|-------|---------|
| Valid signup | still anonymous |
| Valid confirmation link | `login()` as that user |
| Failed confirmation | still anonymous |
| Valid password reset save | still anonymous; person signs in afterwards |
| Authenticated visit to signup / reset / resend | redirect to perfil; do not start a second account |

## Validation rules (forms)

**Alta (`CrearCuentaForm`)**

- Username: required, unique, charset/length of `User.username`; preserve username + email on error.
- Email: required, valid email syntax; duplicates allowed.
- Password: `password1` + `password2`; `AUTH_PASSWORD_VALIDATORS`; mismatch → Spanish error; do not redisplay secrets.

**Reenvío / restablecimiento**

- Field: **Usuario** only.
- Always the same generic success copy to the visitor.
- Side effect (mail) only when the corresponding state table cell is “yes”.

**Nueva contraseña (reset confirm)**

- Same validators + confirmation as signup.
- Old password must stop working after a successful save.

## Display values (not stored separately)

- Login: **Crear cuenta**, **Olvidé mi contraseña**.
- Post-signup: **Revisa tu correo** (do not claim the address is valid beyond format checks).
- Inactive login: cuenta aún no confirmada + path to resend.
- Invalid/expired link: Spanish failure; offer resend for confirmation, restart reset for password.
- Generic resend/reset done: does not say whether the username exists, is pending, or has mail.
