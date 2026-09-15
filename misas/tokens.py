from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailConfirmationTokenGenerator(PasswordResetTokenGenerator):
    key_salt = "misas.email_confirmation"


email_confirmation_token_generator = EmailConfirmationTokenGenerator()
