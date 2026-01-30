import requests

API_KEY = "AIzaSyBibUysdkGMVAdVbU6z9ovdMMlToEq0D0o"

# ---------------- Create a new user ----------------
def register_user(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
    payload = { 
        "email": email,
        "password": password,
        "returnSecureToken": True  
    }

    response = requests.post(url, json=payload)
    data = response.json()

    if "idToken" in data:
        print("✅ User created successfully!")
        print("User UID:", data["localId"])
        return data
    else:
        print("❌ Error creating user:", data.get("error", {}).get("message", "Unknown error"))
        return None

# ---------------- Login existing user ----------------
def login_user(email, password):
    """
    Logs in an existing user with Firebase.
    Returns a dictionary with ID token and UID if successful.
    """
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=payload)
    data = response.json()

    if "idToken" in data:
        print("✅ Login successful!")
        print("User UID:", data["localId"])
        return data
    else:
        print("❌ Login failed:", data.get("error", {}).get("message", "Unknown error"))
        return None

# ---------------- Reset password ----------------
def reset_password(email):
    """
    Sends a password reset email to the user.
    Returns True if email was sent successfully.
    """
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={API_KEY}"
    payload = {
        "email": email,
        "requestType": "PASSWORD_RESET"
    }

    response = requests.post(url, json=payload)
    data = response.json()

    if "email" in data:
        print("✅ Password reset email sent!")
        return True
    else:
        print("❌ Failed to send reset email:", data.get("error", {}).get("message", "Unknown error"))
        return False