import requests
from datetime import datetime

API_KEY = "AIzaSyBibUysdkGMVAdVbU6z9ovdMMlToEq0D0o"
PROJECT_ID = "bank-login-det"
FIRESTORE_ROOT = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"


def _auth_request(path, payload):
    url = f"https://identitytoolkit.googleapis.com/v1/{path}?key={API_KEY}"
    return requests.post(url, json=payload).json()


def _firestore_request(uid, id_token, payload=None, method="GET"):
    url = f"{FIRESTORE_ROOT}/users/{uid}"
    headers = {"Authorization": f"Bearer {id_token}"}
    if method == "PATCH":
        return requests.patch(url, json=payload, headers=headers)
    return requests.get(url, headers=headers)


def _get_fields(data, *keys):
    fields = data.get("fields", {})
    for key in keys:
        fields = fields.get(key, {}).get("mapValue", {}).get("fields", {})
    return fields


def _string_value(text):
    return {"stringValue": str(text)}


def _double_value(number):
    return {"doubleValue": float(number)}


def _map_value(fields):
    return {"mapValue": {"fields": fields}}


def _extract_account_values(fields):
    return {
        "checking": float(fields.get("checking", {}).get("doubleValue", 0.0)),
        "savings": float(fields.get("savings", {}).get("doubleValue", 0.0)),
    }


def register_user(email, password):
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
    payload = {
        "fields": {
            "email": _string_value(email),
            "createdAt": _string_value(datetime.now().isoformat()),
            "accounts": _map_value({
                "checking": _double_value(0.0),
                "savings": _double_value(0.0),
                "creditCard": _double_value(0.0),
            }),
            "profile": _map_value({
                "firstName": _string_value(""),
                "lastName": _string_value(""),
                "phone": _string_value(""),
            }),
        }
    }
    return _firestore_request(uid, id_token, payload, method="PATCH").status_code == 200


def get_user_accounts(uid, id_token):
    response = _firestore_request(uid, id_token)
    if response.status_code != 200:
        return None
    return _extract_account_values(_get_fields(response.json(), "accounts"))


def update_user_accounts(uid, id_token, checking=None, savings=None, credit_card=None):
    fields = {}
    if checking is not None:
        fields["checking"] = _double_value(checking)
    if savings is not None:
        fields["savings"] = _double_value(savings)
    if credit_card is not None:
        fields["creditCard"] = _double_value(credit_card)
    if not fields:
        return False
    payload = {"fields": {"accounts": _map_value(fields)}}
    return _firestore_request(uid, id_token, payload, method="PATCH").status_code == 200


def get_user_by_email(email, id_token):
    url = f"{FIRESTORE_ROOT}:runQuery"
    headers = {"Authorization": f"Bearer {id_token}"}
    query = {
        "structuredQuery": {
            "from": [{"collectionId": "users"}],
            "where": {
                "fieldFilter": {
                    "field": {"fieldPath": "email"},
                    "op": "EQUAL",
                    "value": {"stringValue": email},
                }
            },
            "limit": 1,
        }
    }
    response = requests.post(url, json=query, headers=headers)
    if response.status_code != 200:
        return None
    for result in response.json():
        document = result.get("document")
        if not document:
            continue
        uid = document["name"].split("/")[-1]
        return {"uid": uid, "fields": _get_fields(document)}
    return None


def update_user_profile(uid, first_name, last_name, phone, id_token):
    payload = {
        "fields": {
            "profile": _map_value({
                "firstName": _string_value(first_name),
                "lastName": _string_value(last_name),
                "phone": _string_value(phone),
            })
        }
    }
    return _firestore_request(uid, id_token, payload, method="PATCH").status_code == 200


def get_user_profile(uid, id_token):
    response = _firestore_request(uid, id_token)
    if response.status_code != 200:
        return None
    profile = _get_fields(response.json(), "profile")
    return {
        "firstName": profile.get("firstName", {}).get("stringValue", ""),
        "lastName": profile.get("lastName", {}).get("stringValue", ""),
        "phone": profile.get("phone", {}).get("stringValue", ""),
    }

