from datetime import datetime, timedelta, timezone
import unittest
from types import SimpleNamespace

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from jose import jwt

from app.auth import JWT_ALGORITHM, JWT_SECRET_KEY, create_access_token, get_current_user


class SessionIdentityTests(unittest.TestCase):
    def test_token_rejects_same_id_for_another_account(self):
        token = create_access_token(1, "qa_account")
        session = SimpleNamespace(get=lambda _model, _id: SimpleNamespace(id=1, username="other_account"))
        with self.assertRaises(HTTPException):
            get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token), session)

    def test_legacy_token_is_rejected(self):
        token = jwt.encode({"sub": "1", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)}, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        session = SimpleNamespace(get=lambda _model, _id: SimpleNamespace(id=1, username="other_account"))
        with self.assertRaises(HTTPException):
            get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token), session)

    def test_matching_account_is_accepted(self):
        token = create_access_token(1, "qa_account")
        user = SimpleNamespace(id=1, username="qa_account")
        self.assertIs(get_current_user(HTTPAuthorizationCredentials(scheme="Bearer", credentials=token), SimpleNamespace(get=lambda *_: user)), user)


if __name__ == "__main__":
    unittest.main()
