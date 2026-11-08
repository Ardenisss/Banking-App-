
import requests
from datetime import datetime

API_KEY = AIzaSyBibUysdkGMVAdVbU6z9ovdMMlToEq0D0o
PROJECT_ID = "bank-login-det"
FIRESTORE_ROOT = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"


def auth_request(path, data):
    url = f"https://identitytoolkit.googleapis.com/v1/{path}?key={API_KEY}"
    response = requests.post(url, json=data)
    return response.json()


def firestore_request(uid, id_token, data=None, method="GET"):
    url = f"{FIRESTORE_ROOT}/users/{uid}"
    headers = {"Authorization": f"Bearer {id_token}"}

    if method == "PATCH":
        return requests.patch(url, json=data, headers=headers)

    return requests.get(url, headers=headers)


def get_fields(data, *keys):
    fields = data.get("fields", {})

    for key in keys:
        fields = fields.get(key, {}).get("mapValue", {}).get("fields", {})

    return fields


def string_value(value):
    return {"stringValue": str(value)}


def double_value(value):
    return {"doubleValue": float(value)}


def map_value(fields):
    return {"mapValue": {"fields": fields}}


def extract_account_values(fields):
    return {
        "checking": float(fields.get("checking", {}).get("doubleValue", 0.0)),
        "savings": float(fields.get("savings", {}).get("doubleValue", 0.0)),
    }


def register_user(email, password):
    data = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    return auth_request("accounts:signUp", data)


def login_user(email, password):
    data = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    return auth_request("accounts:signInWithPassword", data)


def reset_password(email):
    data = {
        "email": email,
        "requestType": "PASSWORD_RESET"
    }

    response = auth_request("accounts:sendOobCode", data)
    return "email" in response


def create_user_document(uid, email, id_token):
    data = {
        "fields": {
            "email": string_value(email),
            "createdAt": string_value(datetime.now().isoformat()),
            "accounts": map_value({
                "checking": double_value(0),
                "savings": double_value(0),
                "creditCard": double_value(0)
            }),
            "profile": map_value({
                "firstName": string_value(""),
                "lastName": string_value(""),
                "phone": string_value("")
            })
        }
    }

    response = firestore_request(uid, id_token, data, "PATCH")
    return response.status_code == 200


def get_user_accounts(uid, id_token):
    response = firestore_request(uid, id_token)

    if response.status_code != 200:
        return None

    fields = get_fields(response.json(), "accounts")
    return extract_account_values(fields)


def update_user_accounts(uid, id_token, checking=None, savings=None, credit_card=None):
    accounts = {}

    if checking is not None:
        accounts["checking"] = double_value(checking)

    if savings is not None:
        accounts["savings"] = double_value(savings)

    if credit_card is not None:
        accounts["creditCard"] = double_value(credit_card)

    if len(accounts) == 0:
        return False

    data = {
        "fields": {
            "accounts": map_value(accounts)
        }
    }

    response = firestore_request(uid, id_token, data, "PATCH")
    return response.status_code == 200


def get_user_by_email(email, id_token):
    url = f"{FIRESTORE_ROOT}:runQuery"
    headers = {"Authorization": f"Bearer {id_token}"}

    data = {
        "structuredQuery": {
            "from": [{"collectionId": "users"}],
            "where": {
                "fieldFilter": {
                    "field": {"fieldPath": "email"},
                    "op": "EQUAL",
                    "value": {"stringValue": email}
                }
            },
            "limit": 1
        }
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code != 200:
        return None

    results = response.json()

    for result in results:
        if "document" in result:
            document = result["document"]
            uid = document["name"].split("/")[-1]

            return {
                "uid": uid,
                "fields": get_fields(document)
            }

    return None


def update_user_profile(uid, first_name, last_name, phone, id_token):
    data = {
        "fields": {
            "profile": map_value({
                "firstName": string_value(first_name),
                "lastName": string_value(last_name),
                "phone": string_value(phone)
            })
        }
    }

    response = firestore_request(uid, id_token, data, "PATCH")
    return response.status_code == 200


def get_user_profile(uid, id_token):
    response = firestore_request(uid, id_token)

    if response.status_code != 200:
        return None

    profile = get_fields(response.json(), "profile")

    return {
        "firstName": profile.get("firstName", {}).get("stringValue", ""),
        "lastName": profile.get("lastName", {}).get("stringValue", ""),
        "phone": profile.get("phone", {}).get("stringValue", "")
    }
