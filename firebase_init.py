import requests
from datetime import datetime

API_KEY = "AIzaSyBibUysdkGMVAdVbU6z9ovdMMlToEq0D0o"
PROJECT_ID = "bank-login-det"
FIRESTORE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"


def register_user(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(url, json=payload)
    return response.json()


def login_user(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    response = requests.post(url, json=payload)
    return response.json()


def reset_password(email):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_KEY}"
    payload = {"email": email, "requestType": "PASSWORD_RESET"}
    response = requests.post(url, json=payload)
    return "email" in response.json()


def create_user_document(uid, email, id_token):
    """Create new user document with accounts starting at $0"""
    url = f"{FIRESTORE_URL}/users/{uid}"
    
    payload = {
        "fields": {
            "email": {"stringValue": email},
            "createdAt": {"stringValue": datetime.now().isoformat()},
            "accounts": {
                "mapValue": {
                    "fields": {
                        "checking": {"doubleValue": 0.0},
                        "savings": {"doubleValue": 0.0},
                        "creditCard": {"doubleValue": 0.0}
                    }
                }
            },
            "profile": {
                "mapValue": {
                    "fields": {
                        "firstName": {"stringValue": ""},
                        "lastName": {"stringValue": ""},
                        "phone": {"stringValue": ""}
                    }
                }
            }
        }
    }
    headers = {"Authorization": f"Bearer {id_token}"}
    response = requests.patch(url, json=payload, headers=headers)
    return response.status_code == 200


def get_user_accounts(uid, id_token):
    """Get checking and savings account balances"""
    url = f"{FIRESTORE_URL}/users/{uid}"
    headers = {"Authorization": f"Bearer {id_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        accounts = data.get("fields", {}).get("accounts", {}).get("mapValue", {}).get("fields", {})
        checking = float(accounts.get("checking", {}).get("doubleValue", 0.0))
        savings = float(accounts.get("savings", {}).get("doubleValue", 0.0))
        return {"checking": checking, "savings": savings}
    return None


def get_user_money(uid, id_token):
    """Get total balance (checking + savings combined)"""
    accounts = get_user_accounts(uid, id_token)
    if accounts:
        return accounts["checking"] + accounts["savings"]
    return None


def update_account_balance(uid, account_type, amount, id_token):
    """Update checking or savings balance (account_type = 'checking' or 'savings')"""
    if account_type not in ["checking", "savings"]:
        return False
    
    url = f"{FIRESTORE_URL}/users/{uid}"
    payload = {
        "fields": {
            "accounts": {
                "mapValue": {
                    "fields": {
                        account_type: {"doubleValue": float(amount)}
                    }
                }
            }
        }
    }
    headers = {"Authorization": f"Bearer {id_token}"}
    response = requests.patch(url, json=payload, headers=headers)
    return response.status_code == 200


def update_user_money(uid, amount, id_token):
    """Legacy function - updates checking account"""
    return update_account_balance(uid, "checking", amount, id_token)


def add_money_to_account(uid, account_type, amount, id_token):
    """Add money to checking or savings account"""
    accounts = get_user_accounts(uid, id_token)
    if accounts and account_type in accounts:
        new_balance = accounts[account_type] + amount
        return update_account_balance(uid, account_type, new_balance, id_token)
    return False


def add_money(uid, amount, id_token):
    """Legacy function - adds to checking account"""
    return add_money_to_account(uid, "checking", amount, id_token)


def update_user_profile(uid, first_name, last_name, phone, id_token):
    """Update user profile information"""
    url = f"{FIRESTORE_URL}/users/{uid}"
    payload = {
        "fields": {
            "profile": {
                "mapValue": {
                    "fields": {
                        "firstName": {"stringValue": first_name},
                        "lastName": {"stringValue": last_name},
                        "phone": {"stringValue": phone}
                    }
                }
            }
        }
    }
    headers = {"Authorization": f"Bearer {id_token}"}
    response = requests.patch(url, json=payload, headers=headers)
    return response.status_code == 200


def get_user_profile(uid, id_token):
    """Get user profile information"""
    url = f"{FIRESTORE_URL}/users/{uid}"
    headers = {"Authorization": f"Bearer {id_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        profile = data.get("fields", {}).get("profile", {}).get("mapValue", {}).get("fields", {})
        return {
            "firstName": profile.get("firstName", {}).get("stringValue", ""),
            "lastName": profile.get("lastName", {}).get("stringValue", ""),
            "phone": profile.get("phone", {}).get("stringValue", "")
        }
    return None