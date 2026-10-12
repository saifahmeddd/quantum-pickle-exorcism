"""Focused contract tests for the Firebase Authentication REST adapter."""

import json
import unittest
from unittest.mock import patch

from application.dtos.auth_dto import LoginUserDTO, RegisterUserDTO
from application.exceptions.identity_errors import IdentityProviderUnavailable
from infrastructure.authentication.firebase_auth_rest_provider import (
    FirebaseAuthRestProvider,
)


class FakeUrlResponse:
    """Minimal context-managed HTTP response used without external network I/O."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self):
        return json.dumps(
            {
                "localId": "firebase-user-1",
                "email": "demo@example.com",
                "idToken": "id-token",
                "refreshToken": "refresh-token",
                "expiresIn": "3600",
            }
        ).encode("utf-8")


class FirebaseAuthRestProviderTests(unittest.TestCase):
    """Prove endpoint selection, payload mapping, and required configuration."""

    @patch(
        "infrastructure.authentication.firebase_auth_rest_provider.urlopen",
        return_value=FakeUrlResponse(),
    )
    def test_register_and_login_map_firebase_sessions(self, mocked_urlopen):
        provider = FirebaseAuthRestProvider("web-api-key")

        registered = provider.register(
            RegisterUserDTO("demo@example.com", "Secret123!")
        )
        logged_in = provider.login(LoginUserDTO("demo@example.com", "Secret123!"))

        self.assertEqual(registered, logged_in)
        self.assertEqual(registered.user_id, "firebase-user-1")
        self.assertEqual(registered.expires_in, 3600)

        register_request = mocked_urlopen.call_args_list[0].args[0]
        login_request = mocked_urlopen.call_args_list[1].args[0]
        self.assertIn("accounts:signUp?key=web-api-key", register_request.full_url)
        self.assertIn(
            "accounts:signInWithPassword?key=web-api-key", login_request.full_url
        )
        self.assertEqual(
            json.loads(login_request.data),
            {
                "email": "demo@example.com",
                "password": "Secret123!",
                "returnSecureToken": True,
            },
        )

    def test_web_api_key_is_required_only_when_auth_use_case_runs(self):
        with self.assertRaises(IdentityProviderUnavailable):
            FirebaseAuthRestProvider(None).login(
                LoginUserDTO("demo@example.com", "Secret123!")
            )


if __name__ == "__main__":
    unittest.main()
