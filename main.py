"""Main app module for the ArdenBank authentication flow."""

import time

from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp

# Firebase helper functions are imported from firebase_init.py.
# These functions perform authentication and Firestore data operations.
from firebase_init import (
    register_user,
    login_user,
    reset_password,
    create_user_document,
    update_user_profile,
    get_user_accounts,
    get_user_profile,
)


def check_password(password):
    # Simple password validation rules used during registration.
    # This ensures passwords are at least 8 chars, include a digit,
    # and include an uppercase letter.
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number"
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    return True, ""


def _extract_error(response, fallback):
    # Read the Firebase error message from the API response.
    # If the response does not contain a readable error, return fallback.
    return response.get("error", {}).get("message", fallback)


def store_user(user_data):
    # Keep the current logged-in user data in the Kivy App instance.
    # This is used later by other screens that need the user ID and token.
    app = App.get_running_app()
    app.user = user_data
    app.user_id = user_data.get("localId")
    app.token = user_data.get("idToken")


class AuthBackground(FloatLayout):
    # Background container used by auth screens for layout styling.
    pass


class AuthScreen(Screen):
    # Base screen for any authentication-related UI.
    # Provides a shared error panel and helper methods.
    def show_error(self, message):
        error_box = self.ids.error_box
        self.ids.error_message.text = message
        Animation(height=dp(60), duration=0.3).start(error_box)
        Clock.schedule_once(self.hide_error, 4)

    def hide_error(self, dt=None):
        Animation(height=0, duration=0.3).start(self.ids.error_box)


class LoginScreen(AuthScreen):
    email_input = ObjectProperty(None)
    password_input = ObjectProperty(None)

    # Handle the login button press.
    # Calls Firebase sign-in and switches to dashboard on success.
    def on_login_pressed(self):
        email = self.email_input.text
        password = self.password_input.text
        if not email or not password:
            self.show_error("Please enter both email and password")
            return

        try:
            response = login_user(email, password)
            if "idToken" in response:
                store_user(response)
                self.manager.current = "dashboard"
                return
            self.show_error(_extract_error(response, "Invalid email or password"))
        except Exception as exc:
            self.show_error(f"Error: {exc}")

    def on_forgot_pressed(self):
        self.manager.current = "reset_password"

    def on_register_pressed(self):
        self.manager.current = "register"


class RegisterScreen(AuthScreen):
    # Register screen fields connect to the Kivy layout via ObjectProperty.
    signup_email = ObjectProperty(None)
    signup_password = ObjectProperty(None)
    confirm_password = ObjectProperty(None)

    def on_register_submit(self):
        email = self.signup_email.text
        password = self.signup_password.text
        confirm_password = self.confirm_password.text

        if not email or not password or not confirm_password:
            self.show_error("Please fill all fields")
            return

        valid, message = check_password(password)
        if not valid:
            self.show_error(message)
            return

        if password != confirm_password:
            self.show_error("Passwords do not match")
            return

        try:
            response = register_user(email, password)
            if "idToken" not in response:
                self.show_error(_extract_error(response, "Registration failed"))
                return
            
            store_user(response)
            if create_user_document(app.user_id, email, app.token):
                self.manager.current = "profile_setup"
            else:
                self.show_error("Failed to create user profile")
        except Exception as exc:
            self.show_error(f"Error: {exc}")


class ProfileSetupScreen(AuthScreen):
    # Screen for completing optional profile fields after sign-up.
    first_name_field = ObjectProperty(None)
    last_name_field = ObjectProperty(None)
    phone_field = ObjectProperty(None)

    def on_profile_complete(self):
        first_name = self.first_name_field.text
        last_name = self.last_name_field.text
        phone = self.phone_field.text

        if not any([first_name, last_name, phone]):
            self.manager.current = "dashboard"
            return

        app = App.get_running_app()
        if update_user_profile(app.user_id, first_name, last_name, phone, app.token):
            self.manager.current = "dashboard"
        else:
            self.show_error("Failed to save profile")

    def on_skip_pressed(self):
        self.manager.current = "dashboard"


class MenuScreen(Screen):
    # Base screen for pages that can open the app menu.
    def open_menu(self):
        if not getattr(self, "menu_popup", None):
            content = BoxLayout(orientation="vertical")
            content.add_widget(Button(text="Profile", on_release=self.on_profile))
            content.add_widget(Button(text="Help/Faq", on_release=self.on_help))
            content.add_widget(Button(text="Logout", on_release=self.on_logout))
            self.menu_popup = Popup(
                title="Menu",
                content=content,
                size_hint=(None, None),
                size=(dp(200), dp(150)),
                auto_dismiss=True,
            )
        self.menu_popup.open()

    def on_profile(self, instance):
        print("Profile")
        self.menu_popup.dismiss()

    def on_help(self, instance):
        print("Help/Faq")
        self.menu_popup.dismiss()

    def on_logout(self, instance):
        app = App.get_running_app()
        app.user = None
        app.user_id = None
        app.token = None
        self.menu_popup.dismiss()
        if self.manager:
            self.manager.current = "login"


class DashboardScreen(MenuScreen):
    # Dashboard screen shows the user's account balances and greeting.
    _last_fetch_time = 0
    _fetch_interval = 60

    def on_enter(self):
        app = App.get_running_app()
        if not (app.user_id and app.token):
            print("User not authenticated")
            return

        # Limit refreshes so the dashboard is not reloaded too often.
        if time.time() - self._last_fetch_time < self._fetch_interval:
            return

        self._last_fetch_time = time.time()
        accounts = get_user_accounts(app.user_id, app.token)
        if accounts is None:
            create_user_document(
                app.user_id,
                app.user.get("email", "unknown@example.com"),
                app.token,
            )
            accounts = get_user_accounts(app.user_id, app.token)

        profile = get_user_profile(app.user_id, app.token) or {}
        first_name = profile.get("firstName", "").strip()
        last_name = profile.get("lastName", "").strip()
        if not (first_name or last_name):
            first_name = app.user.get("email", "User").split("@")[0]
        self.ids.welcome_label.text = f"Hello, {first_name} {last_name}".strip() or "Hello!"

        if accounts:
            checking = accounts.get("checking", 0)
            savings = accounts.get("savings", 0)
            total = checking + savings
            self.ids.user_balance.text = f"${total:,.2f}"
            self.ids.checking_balance.text = f"${checking:,.2f}"
            self.ids.savings_balance.text = f"${savings:,.2f}"


class SendMoneyScreen(MenuScreen):
    # Simple calculator-style screen for building transfer amounts.
    def append_digit(self, digit):
        current = (self.ids.amount_input.text or "$0").lstrip("$")
        if digit == "." and "." in current:
            return
        self.ids.amount_input.text = f"${current if current != '0' else ''}{digit}" if digit != "." else f"${current or '0'}."

    def delete_digit(self):
        text = self.ids.amount_input.text.lstrip("$")[:-1]
        self.ids.amount_input.text = f"${text or '0'}"

    def clear_amount(self):
        self.ids.amount_input.text = "$0"

    def on_action(self, action):
        print(f"{action} pressed")


class PasswordResetScreen(AuthScreen):
    # Handle the reset password flow from the email input screen.
    reset_email_field = ObjectProperty(None)

    def on_reset_submit(self):
        email = self.reset_email_field.text
        if not email:
            self.show_error("Please enter your email address")
            return

        try:
            if reset_password(email):
                self.show_error("Check your email for password reset link")
                Clock.schedule_once(lambda dt: self._go_to_login(), 2)
            else:
                self.show_error("No account found with this email")
        except Exception as exc:
            self.show_error(f"Error: {exc}")

    def _go_to_login(self):
        self.manager.current = "login"
        self.reset_email_field.text = ""

    def on_back_pressed(self):
        self._go_to_login()


class BankApp(App):
    # The main application object stores the current user session and loads
    # the Kivy UI definition from Screens/main.kv.
    user = None
    user_id = None
    token = None

    def build(self):
        return Builder.load_file("Screens/main.kv")


if __name__ == "__main__":
    BankApp().run()
