from django.contrib.auth.tokens import PasswordResetTokenGenerator


class ActivationTokenGenerator(PasswordResetTokenGenerator):

    """
      Activation token generator for user accounts.

      This builds on Django's PasswordResetTokenGenerator to create time-bound
      tokens that you can use in account activation links.
    """

    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.is_active}"


account_activation_token = ActivationTokenGenerator()
