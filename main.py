# main.py - ArdenBank Authentication System
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.floatlayout import FloatLayout
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp

from hover import HoverLabel
from firebase_init import register_user, login_user, reset_password, create_user_document



class AuthBackground(FloatLayout):
    """Shared background component for login and register screens."""
    pass


# -------- Helper Functions --------
def get_input_text(input_widget):
    """Safely retrieve text from input widget."""
    return input_widget.text if input_widget else ""


def validate_password_strength(password):
    """Validate password meets security requirements."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one number"
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    return True, ""


# -------- Base Screen Class --------
class AuthScreen(Screen):
    """Base class for authentication screens with shared error handling."""
    
    def show_error(self, message):
        """Display error notification."""
        error_box = self.ids.error_box
        error_message = self.ids.error_message
        error_message.text = message
        
        anim = Animation(height=dp(60), duration=0.3)
        anim.start(error_box)
        Clock.schedule_once(self.hide_error, 4)
    
    def hide_error(self, dt=None):
        """Hide error notification."""
        error_box = self.ids.error_box
        anim = Animation(height=0, duration=0.3)
        anim.start(error_box)


class LoginScreen(AuthScreen):
    """User login interface with email and password validation."""
    username_input = ObjectProperty(None)
    password_input = ObjectProperty(None)
    login_btn = ObjectProperty(None)
    forgot_btn = ObjectProperty(None)
    register_btn = ObjectProperty(None)

    def on_login_pressed(self):
        """Handle login button press with Firebase authentication."""
        email = get_input_text(self.username_input)
        pw = get_input_text(self.password_input)
        
        if not email or not pw:
            self.show_error("Please enter both email and password")
            return
        
        try:
            response = login_user(email, pw)
            
            # Check if login succeeded
            if "idToken" in response:
                user = response
                app = App.get_running_app()
                app.current_user = user
                app.current_user_id = user.get('localId')
                app.current_id_token = user.get('idToken')
                self.manager.current = 'dashboard'
            # Check if there's an error in the response
            elif "error" in response:
                error_msg = response.get("error", {}).get("message", "Invalid email or password")
                self.show_error(error_msg)
            else:
                self.show_error("Login failed")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def on_forgot_pressed(self):
        """Navigate to password reset screen."""
        self.manager.current = 'reset_password'

    def on_register_pressed(self):
        """Navigate to registration screen."""
        self.manager.current = 'register'


class RegisterScreen(AuthScreen):
    """User registration interface with password validation."""
    new_username_input = ObjectProperty(None)
    new_password_input = ObjectProperty(None)
    confirm_password_input = ObjectProperty(None)
    submit_btn = ObjectProperty(None)
    back_btn = ObjectProperty(None)

    def on_register_submit(self):
        """Handle registration with validation and Firebase."""
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
            
            # Check if registration succeeded
            if "idToken" in response:
                user = response
                uid = user.get('localId')
                id_token = user.get('idToken')
                
                # Create Firestore document for new user
                success = create_user_document(uid, email, id_token)
                
                if success:
                    app = App.get_running_app()
                    app.current_user = user
                    app.current_user_id = uid
                    app.current_id_token = id_token
                    self.manager.current = 'dashboard'
                else:
                    self.show_error("Failed to create user profile")
            # Check if there's an error in the response
            elif "error" in response:
                error_msg = response.get("error", {}).get("message", "Registration failed")
                self.show_error(error_msg)
            else:
                self.show_error("Registration failed")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")


class PasswordResetScreen(AuthScreen):
    """Password reset screen with email verification."""
    reset_email_input = ObjectProperty(None)

    def on_reset_submit(self):
        """Handle password reset submission."""
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
                Clock.schedule_once(lambda dt: self.back_to_login(), 2)
            else:
                self.show_error("No account found with this email")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def back_to_login(self):
        """Return to login screen."""
        self.manager.current = 'login'
        self.reset_email_input.text = ""

    def on_back_pressed(self):
        """Navigate back to login."""
        self.manager.current = 'login'
        self.reset_email_input.text = ""


class DashboardScreen(Screen):
    """User dashboard after successful authentication."""
    pass


class BankApp(App):
    """ArdenBank application main class."""
    current_user = None
    current_user_id = None
    current_id_token = None

    def build(self):
        return Builder.load_file('Screens/main.kv')


if __name__ == "__main__":
    BankApp().run()
