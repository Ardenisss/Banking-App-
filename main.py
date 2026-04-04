"""ArdenBank Authentication System - Main Application Module.

Provides user interface for registration, login, password reset, and dashboard.
Uses Firebase for authentication and Firestore for data persistence.
"""
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.floatlayout import FloatLayout
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from hover import HoverLabel
from firebase_init import register_user, login_user, reset_password, create_user_document, update_user_profile, get_user_accounts, get_user_profile


class AuthBackground(FloatLayout):
    pass


def get_input_text(input_widget):
    return input_widget.text if input_widget else ""


def validate_password_strength(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number"
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    return True, ""


def store_user_in_app(user_data):
    app = App.get_running_app()
    app.current_user = user_data
    app.current_user_id = user_data.get('localId')
    app.current_id_token = user_data.get('idToken')


class AuthScreen(Screen):
    def show_error(self, message):
        error_box = self.ids.error_box
        error_message = self.ids.error_message
        error_message.text = message
        anim = Animation(height=dp(60), duration=0.3)
        anim.start(error_box)
        Clock.schedule_once(self.hide_error, 4)
    
    def hide_error(self, dt=None):
        error_box = self.ids.error_box
        anim = Animation(height=0, duration=0.3)
        anim.start(error_box)


class LoginScreen(AuthScreen):
    username_input = ObjectProperty(None)
    password_input = ObjectProperty(None)
    login_btn = ObjectProperty(None)
    forgot_btn = ObjectProperty(None)
    register_btn = ObjectProperty(None)

    def on_login_pressed(self):
        email = get_input_text(self.username_input)
        pw = get_input_text(self.password_input)
        if not email or not pw:
            self.show_error("Please enter both email and password")
            return
        try:
            response = login_user(email, pw)
            if "idToken" in response:
                store_user_in_app(response)
                self.manager.current = 'dashboard'
            elif "error" in response:
                error_msg = response.get("error", {}).get("message", "Invalid email or password")
                self.show_error(error_msg)
            else:
                self.show_error("Login failed")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def on_forgot_pressed(self):
        self.manager.current = 'reset_password'

    def on_register_pressed(self):
        self.manager.current = 'register'


class RegisterScreen(AuthScreen):
    new_username_input = ObjectProperty(None)
    new_password_input = ObjectProperty(None)
    confirm_password_input = ObjectProperty(None)
    submit_btn = ObjectProperty(None)
    back_btn = ObjectProperty(None)

    def on_register_submit(self):
        email = get_input_text(self.new_username_input)
        pw = get_input_text(self.new_password_input)
        pwc = get_input_text(self.confirm_password_input)

        if not email or not pw or not pwc:
            self.show_error("Please fill all fields")
            return

        is_valid, message = validate_password_strength(pw)
        if not is_valid:
            self.show_error(message)
            return

        if pw != pwc:
            self.show_error("Passwords do not match")
            return

        try:
            response = register_user(email, pw)
            if "idToken" in response:
                uid = response.get('localId')
                id_token = response.get('idToken')
                success = create_user_document(uid, email, id_token)
                if success:
                    store_user_in_app(response)
                    # Go to profile setup screen instead of dashboard
                    self.manager.current = 'profile_setup'
                else:
                    self.show_error("Failed to create user profile")
            elif "error" in response:
                error_msg = response.get("error", {}).get("message", "Registration failed")
                self.show_error(error_msg)
            else:
                self.show_error("Registration failed")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")


class ProfileSetupScreen(AuthScreen):
    first_name_input = ObjectProperty(None)
    last_name_input = ObjectProperty(None)
    phone_input = ObjectProperty(None)
    skip_btn = ObjectProperty(None)
    complete_btn = ObjectProperty(None)

    def on_profile_complete(self):
        """Save profile and go to dashboard (only if something is filled in)"""
        first_name = get_input_text(self.first_name_input)
        last_name = get_input_text(self.last_name_input)
        phone = get_input_text(self.phone_input)

        try:
            # Only update if at least one field has content
            if first_name or last_name or phone:
                app = App.get_running_app()
                uid = app.current_user_id
                id_token = app.current_id_token
                
                success = update_user_profile(uid, first_name, last_name, phone, id_token)
                if not success:
                    self.show_error("Failed to save profile")
                    return
            
            self.manager.current = 'dashboard'
        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def on_skip_pressed(self):
        """Skip profile setup and go to dashboard"""
        self.manager.current = 'dashboard'



class DashboardScreen(Screen):
    def on_enter(self):
        try:
            uid, id_token = getUserIDs()
            accounts = get_user_accounts(uid, id_token)
            profile = get_user_profile(uid, id_token)

            if profile:
                first_name = profile.get("firstName", "")
                last_name = profile.get("lastName", "")
                if first_name or last_name:
                    self.ids.welcome_label.text = f"Hello, {first_name} {last_name}".strip()
                else:
                    self.ids.welcome_label.text = "Hello!"

            if accounts:
                checking = accounts["checking"]
                savings = accounts["savings"]
                total = checking + savings
                
                # Format as currency
                checking_formatted = f"${checking:,.2f}"
                savings_formatted = f"${savings:,.2f}"
                total_formatted = f"${total:,.2f}"
                
                # Set the label text
                self.ids.user_balance.text = total_formatted
                self.ids.checking_balance.text = checking_formatted
                self.ids.savings_balance.text = savings_formatted
        
        except Exception as e:
            print(f"Error loading balances: {e}")        

    def open_menu(self):
        if not hasattr(self, 'menu_popup') or self.menu_popup is None:
            content = BoxLayout(orientation='vertical')
            profile_btn = Button(text='Profile', on_release=self.on_profile)
            help_btn = Button(text='Help/Faq', on_release=self.on_help)
            logout_btn = Button(text='Logout', on_release=self.on_logout)
            content.add_widget(profile_btn)
            content.add_widget(help_btn)
            content.add_widget(logout_btn)
            self.menu_popup = Popup(title='Menu', content=content, size_hint=(None, None), size=(dp(200), dp(150)), auto_dismiss=True)
        self.menu_popup.open()

    def on_profile(self, instance):
        print("Profile")
        self.menu_popup.dismiss()

    def on_help(self, instance):
        print("Help/Faq")
        self.menu_popup.dismiss()

    def on_logout(self, instance):
        print("Logout")
        self.menu_popup.dismiss()        


class PasswordResetScreen(AuthScreen):
    reset_email_input = ObjectProperty(None)

    def on_reset_submit(self):
        email = get_input_text(self.reset_email_input)
        if not email:
            self.show_error("Please enter your email address")
            return
        if '@' not in email:
            self.show_error("Please enter a valid email address")
            return
        try:
            success = reset_password(email)
            if success:
                self.show_error("Check your email for password reset link")
                Clock.schedule_once(lambda dt: self._go_to_login(), 2)
            else:
                self.show_error("No account found with this email")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def _go_to_login(self):
        self.manager.current = 'login'
        self.reset_email_input.text = ""

    def on_back_pressed(self):
        self._go_to_login()


class BankApp(App):
    current_user = None
    current_user_id = None
    current_id_token = None

    def build(self):
        return Builder.load_file('Screens/main.kv')


if __name__ == "__main__":
    BankApp().run()
