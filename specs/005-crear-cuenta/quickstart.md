# Quickstart: Crear cuenta, verificar correo y recuperar contraseña

Validate this feature after implementation. Field/state rules are in [data-model.md](./data-model.md); HTTP/mail behavior is in [contracts/cuenta.md](./contracts/cuenta.md).

## Prerequisites

- Python 3.12, project virtualenv, dependencies from `requirements.txt`
- Env vars already used by the app (`DJANGO_SECRET_KEY`, and `DEFAULT_FROM_EMAIL` once set)
- Tests use locmem mail (no inbox required). Browser pass can read confirmation/reset URLs from the runserver console (`console.EmailBackend`)

## Automated checks

From the repo root:

```bash
python manage.py test misas
```

Expect existing temple/service and navbar/perfil tests to keep passing, plus coverage of:

- Anonymous GET `/accounts/login/` → HTML contains **Crear cuenta** → `/accounts/crear-cuenta/` and **Olvidé mi contraseña** → `/accounts/password_reset/`; still Spanish **Iniciar sesión**
- Authenticated GET login / crear-cuenta / password_reset → redirect away from guest forms
- GET crear-cuenta → `200`; labels Usuario, Correo de contacto, contraseña + confirmación
- POST crear-cuenta invalid (empty, bad email, duplicate username, weak/mismatched password) → no new `User`, `len(mail.outbox) == 0`, secrets not redisplayed
- POST crear-cuenta valid → `User` with that username/email, `is_active is False`, not staff; one outbound mail; client **not** authenticated; follow redirect to “revisa tu correo”
- `Client.login` with the new credentials → fails; GET perfil and GET/POST servicios editor → login redirect; no new `Servicio`
- GET confirm URL from the mail → user `is_active is True`; client authenticated; `302`/`200` on perfil showing username + email, not password
- Second GET of the same confirm URL → does not error into a new pending user; password-reset confirm MUST NOT accept that token
- POST login while still pending → Spanish unconfirmed copy; resend path present
- POST reenviar-confirmacion with unknown username vs pending username → same generic visitor copy; mail only for pending+email
- POST password_reset with an **active** user who has email → generic done; one reset mail; confirm link sets a new valid password; old password fails; new password logs in
- POST password_reset with pending / unknown / no-email → generic done; no (useful) mail; password unchanged
- Existing `create_user` (active) still logs in and reaches the servicios editor as today

## Manual browser pass (required for UI)

1. Sign out. Open **Iniciar sesión**. Confirm **Crear cuenta** and **Olvidé mi contraseña** on the card, same cream/gold language, no English Sign up / Forgot password. Confirm they are **not** in the navbar.
2. Open **Crear cuenta**, use **Iniciar sesión** to go back without creating an account.
3. Submit invalid alta (short password, mismatch, duplicate if you already have a user) → Spanish errors, username/email remain, passwords empty.
4. Submit a valid alta → **Revisa tu correo**, still a visitor in the navbar (**Iniciar sesión**). Try logging in with those credentials → unconfirmed message.
5. Copy the confirmation link from the console mail. Open it → land on Mi perfil identified; names **No registrado**; email visible; no password. Navbar shows **Mi perfil**.
6. Open the same confirmation link again → Spanish invalid/already-confirmed handling, not a crash.
7. Narrow the viewport on login and signup; collapse menu still has **Iniciar sesión** only in the bar.
8. Log out. **Olvidé mi contraseña**, enter the username, open the reset link from the console, set a valid new password, sign in with it. Confirm the old password fails.
9. As an existing staff/superuser created before this feature, sign in without any confirmation mail.

## Done when

Tests above pass and the browser pass matches the spec (signup without session, confirm then collaborator access, username-keyed reset, Spanish themed pages).
