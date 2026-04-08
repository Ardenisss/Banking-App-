import requests
from datetime import datetime

API_KEY = "AIzaSyBibUysdkGMVAdVbU6z9ovdMMlToEq0D0o"
PROJECT_ID = "bank-login-det"
FIRESTORE_ROOT = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"


def _auth_request(path, payload):
    # Send a request to Firebase Authentication REST API.
    # Used for sign-up, sign-in, and password reset operations.
    url = f"https://identitytoolkit.googleapis.com/v1/{path}?key={API_KEY}"
    return requests.post(url, json=payload).json()


def _firestore_request(uid, id_token, payload=None, method="GET"):
    # Send a GET or PATCH request to the user Firestore document.
    # The id_token is used for Firebase authentication.
    """Get or update the user Firestore document."""
    url = f"{FIRESTORE_ROOT}/users/{uid}"
    headers = {"Authorization": f"Bearer {id_token}"}
    if method == "GET":
        return requests.get(url, headers=headers)
    return requests.patch(url, json=payload, headers=headers)


def _get_fields(data, *keys):
    # Walk through nested Firestore mapValue fields safely.
    # Firestore returns deeply nested dictionaries for document fields.
    """Traverse nested Firestore mapValue fields safely."""
    fields = data.get("fields", {})
    for key in keys:
        fields = fields.get(key, {}).get("mapValue", {}).get("fields", {})
    return fields


def _string_value(value):
    return {"stringValue": str(value)}


def _double_value(value):
    return {"doubleValue": float(value)}


def register_user(email, password):
    # Create a new Firebase user account with email and password.
    return _auth_request("accounts:signUp", {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    })


def login_user(email, password):
    return _auth_request("accounts:signInWithPassword", {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    })


def reset_password(email):
    response = _auth_request("accounts:sendOobCode", {
        "email": email,
        "requestType": "PASSWORD_RESET",
    })
    return "email" in response


def create_user_document(uid, email, id_token):
    # Create a Firestore document for a new user.
    # This sets default checking/savings balances and an empty profile.
    payload = {
        "fields": {
            "email": _string_value(email),
            "createdAt": _string_value(datetime.now().isoformat()),
            "accounts": {
                "mapValue": {
                    "fields": {
                        "checking": _double_value(0.0),
                        "savings": _double_value(0.0),
                        "creditCard": _double_value(0.0),
                    }
                }
            },
            "profile": {
                "mapValue": {
                    "fields": {
                        "firstName": _string_value(""),
                        "lastName": _string_value(""),
                        "phone": _string_value(""),
                    }
                }
            },
        }
    }
    return _firestore_request(uid, id_token, payload, method="PATCH").status_code == 200


def get_user_accounts(uid, id_token):
    """Return checking and savings balances."""
    response = _firestore_request(uid, id_token)
    if response.status_code != 200:
        return None

    accounts = _get_fields(response.json(), "accounts")
    return {
        "checking": float(accounts.get("checking", {}).get("doubleValue", 0.0)),
        "savings": float(accounts.get("savings", {}).get("doubleValue", 0.0)),
    }


def update_user_profile(uid, first_name, last_name, phone, id_token):
    """Save profile fields to Firestore."""
    payload = {
        "fields": {
            "profile": {
                "mapValue": {
                    "fields": {
                        "firstName": _string_value(first_name),
                        "lastName": _string_value(last_name),
                        "phone": _string_value(phone),
                    }
                }
            }
        }
    }
    return _firestore_request(uid, id_token, payload, method="PATCH").status_code == 200


def get_user_profile(uid, id_token):
    # Fetch the user's profile fields from Firestore.
    response = _firestore_request(uid, id_token)
    if response.status_code != 200:
        return None

    profile = _get_fields(response.json(), "profile")
    return {
        "firstName": profile.get("firstName", {}).get("stringValue", ""),
        "lastName": profile.get("lastName", {}).get("stringValue", ""),
        "phone": profile.get("phone", {}).get("stringValue", ""),
    }
