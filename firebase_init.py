import requests

API_KEY = "AIzaSyBibUysdkGMVAdVbU6z9ovdMMlToEq0D0o"
PROJECT_ID = "bank-login-det"
FIRESTORE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"


def register_user(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}

    response = requests.post(url, json=payload)
    data = response.json()

    if "idToken" in data:
        return data
    else:
        # Return the full response so caller can see the error
        return data

def login_user(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}

    response = requests.post(url, json=payload)
    data = response.json()

    if "idToken" in data:
        return data
    else:
        # Return the full response so caller can see the error
        return data

def reset_password(email):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_KEY}"
    payload = {"email": email,"requestType": "PASSWORD_RESET"}

    response = requests.post(url, json=payload)
    data = response.json()

    if "email" in data:
        return True
    else:
        return False


# -------- FIRESTORE FUNCTIONS (using idToken) --------

def create_user_document(uid, email, id_token):
    """Create a new user document when they register"""
    url = f"{FIRESTORE_URL}/users/{uid}"
    
    payload = {
        "fields": {
            "email": {"stringValue": email},
            "money": {"integerValue": "0"}
        }
    }
    
    headers = {"Authorization": f"Bearer {id_token}"}
    response = requests.patch(url, json=payload, headers=headers)
    
    return response.status_code == 200


def get_user_money(uid, id_token):
    """Get a user's money from Firestore"""
    url = f"{FIRESTORE_URL}/users/{uid}"
    
    headers = {"Authorization": f"Bearer {id_token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        money_field = data.get("fields", {}).get("money", {})
        return int(money_field.get("integerValue", 0))
    else:
        return None


def update_user_money(uid, amount, id_token):
    """Update a user's money in Firestore"""
    url = f"{FIRESTORE_URL}/users/{uid}"
    
    payload = {
        "fields": {
            "money": {"integerValue": str(amount)}
        }
    }
    
    headers = {"Authorization": f"Bearer {id_token}"}
    response = requests.patch(url, json=payload, headers=headers)
    
    return response.status_code == 200


def add_money(uid, amount, id_token):
    """Add money to user's account"""
    current = get_user_money(uid, id_token)
    
    if current is not None:
        new_amount = current + amount
        return update_user_money(uid, new_amount, id_token)
    
    return False