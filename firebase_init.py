import os
import re
from datetime import datetime, timezone
from typing import Any

import requests


# Firebase web API keys are project identifiers, not server secrets.
# Keep the key out of source control and set FIREBASE_API_KEY in the environment.
API_KEY = os.getenv("FIREBASE_API_KEY")
PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", "bank-login-det")

if not API_KEY:
    raise RuntimeError(
        "FIREBASE_API_KEY is not set. Set it as an environment variable "
        "before running this application."
    )

FIRESTORE_ROOT = (
    "https://firestore.googleapis.com/v1/projects/"
    f"{PROJECT_ID}/databases/(default)/documents"
)
IDENTITY_TOOLKIT_ROOT = "https://identitytoolkit.googleapis.com/v1"
REQUEST_TIMEOUT = (5, 15)  # connect timeout, read timeout

_session = requests.Session()


class FirebaseError(RuntimeError):
    """Raised when a Firebase request fails."""


def _json_response(response: requests.Response) -> dict[str, Any]:
    """Parse a Firebase JSON response and raise a safe, useful error on failure."""
    try:
        data = response.json()
    except ValueError:
        data = {}

    if not response.ok:
        # Do not include tokens, passwords, or full request URLs in exceptions.
        error = data.get("error", {})
        message = error.get("message", "Firebase request failed")
        raise FirebaseError(f"Firebase returned HTTP {response.status_code}: {message}")

    return data


def _auth_request(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    url = f"{IDENTITY_TOOLKIT_ROOT}/{path}"
    response = _session.post(
        url,
        params={"key": API_KEY},
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    return _json_response(response)


def _validate_uid(uid: str) -> str:
    """Reject malformed document IDs before constructing a Firestore URL."""
    if not isinstance(uid, str) or not uid or not re.fullmatch(r"[A-Za-z0-9_-]+", uid):
        raise ValueError("A valid Firebase user UID is required.")
    return uid


def _validate_id_token(id_token: str) -> str:
    if not isinstance(id_token, str) or not id_token.strip():
        raise ValueError("A valid Firebase ID token is required.")
    return id_token.strip()


def _firestore_request(
    uid: str,
    id_token: str,
    payload: dict[str, Any] | None = None,
    method: str = "GET",
) -> dict[str, Any]:
    uid = _validate_uid(uid)
    id_token = _validate_id_token(id_token)

    if method not in {"GET", "PATCH"}:
        raise ValueError("Unsupported Firestore request method.")

    url = f"{FIRESTORE_ROOT}/users/{uid}"
    headers = {"Authorization": f"Bearer {id_token}"}

    if method == "PATCH":
        response = _session.patch(
            url,
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
    else:
