"""Focused tests for the Firebase authentication boundary."""

import unittest
from unittest.mock import patch

from application.exceptions.authentication_failed import AuthenticationFailed
from application.interfaces.authentication import AuthenticatedUser
from domain.value_objects.user_id import UserId
from infrastructure.authentication.firebase_token_verifier import FirebaseTokenVerifier
from presentation.middleware.authentication import authenticate


class StubVerifier:
    """Return a known identity while recording the received bearer token."""

    def __init__(self):
        self.token = None

    def verify(self, token: str) -> AuthenticatedUser:
        self.token = token
        return AuthenticatedUser(UserId("verified-user"), "user@example.com")


class AuthenticationTests(unittest.TestCase):
    """Prove transport parsing and Firebase claim mapping independently."""

    def test_bearer_header_is_required_and_parsed(self):
        verifier = StubVerifier()
        user = authenticate({"Authorization": "Bearer token-value"}, verifier)
        self.assertEqual(user.id.value, "verified-user")
        self.assertEqual(verifier.token, "token-value")

        for headers in [{}, {"Authorization": "Basic abc"}, {"Authorization": "Bearer "}]:
            with self.subTest(headers=headers):
                with self.assertRaises(AuthenticationFailed):
                    authenticate(headers, verifier)

    @patch("firebase_admin.auth.verify_id_token")
    def test_firebase_claims_become_authenticated_user(self, verify_id_token):
        verify_id_token.return_value = {
            "uid": "firebase-uid", "email": "owner@example.com"
        }
        user = FirebaseTokenVerifier().verify("signed-token")
        verify_id_token.assert_called_once_with("signed-token", check_revoked=True)
        self.assertEqual(user.id.value, "firebase-uid")
        self.assertEqual(user.email, "owner@example.com")

    @patch("firebase_admin.auth.verify_id_token")
    def test_missing_uid_is_rejected(self, verify_id_token):
        verify_id_token.return_value = {"email": "owner@example.com"}
        with self.assertRaises(AuthenticationFailed):
            FirebaseTokenVerifier().verify("signed-token")


if __name__ == "__main__":
    unittest.main()
