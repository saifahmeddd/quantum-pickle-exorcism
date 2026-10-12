"""Safe application failures for credential-based identity use cases."""


class RegistrationFailed(Exception):
    """The identity provider rejected a registration attempt."""


class LoginFailed(Exception):
    """The identity provider rejected a login attempt."""


class IdentityProviderUnavailable(Exception):
    """Authentication could not run because its external provider failed."""
