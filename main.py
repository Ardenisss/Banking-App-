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
from firebase_init import register_user, login_user, reset_password


class AuthBackground(FloatLayout):
    """Shared background component for login and register screens."""
    pass


class LoginScreen(Screen):
    """User login interface with email and password validation."""
    username_input = ObjectProperty(None)
    password_input = ObjectProperty(None)
    login_btn = ObjectProperty(None)
    forgot_btn = ObjectProperty(None)
    register_btn = ObjectProperty(None)

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

    def on_login_pressed(self):
        """Handle login button press with Firebase authentication."""
        email = self.username_input.text if self.username_input else ""
        pw = self.password_input.text if self.password_input else ""
        
        if not email or not pw:
            self.show_error("Please enter both email and password")
            return
        
        try:
            user = login_user(email, pw)
            if user:
                App.get_running_app().current_user = user
                self.manager.current = 'dashboard'
            else:
                self.show_error("Invalid email or password")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def on_forgot_pressed(self):
        """Navigate to password reset screen."""
        self.manager.current = 'reset_password'

    def on_register_pressed(self):
        """Navigate to registration screen."""
        self.manager.current = 'register'


class RegisterScreen(Screen):
    """User registration interface with password validation."""
    new_username_input = ObjectProperty(None)
    new_password_input = ObjectProperty(None)
    confirm_password_input = ObjectProperty(None)
    submit_btn = ObjectProperty(None)
    back_btn = ObjectProperty(None)

    def is_password_weak(self, password):
        """Validate password strength (8+ chars, 1 number, 1 uppercase)."""
        if len(password) < 8:
            return True, "Password must be at least 8 characters long"
        if not any(char.isdigit() for char in password):
            return True, "Password must contain at least one number"
        if not any(char.isupper() for char in password):
            return True, "Password must contain at least one uppercase letter"
        return False, ""

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

    def on_register_submit(self):
        """Handle registration with validation and Firebase."""
        email = self.new_username_input.text if self.new_username_input else ""
        pw = self.new_password_input.text if self.new_password_input else ""
        pwc = self.confirm_password_input.text if self.confirm_password_input else ""

        if not email or not pw or not pwc:
            self.show_error("Please fill all fields")
            return

        is_weak, weak_message = self.is_password_weak(pw)
        if is_weak:
            self.show_error(weak_message)
            return

        if pw != pwc:
            self.show_error("Passwords do not match")
            return

        try:
            user = register_user(email, pw)
            if user:
                App.get_running_app().current_user = user
                self.manager.current = 'dashboard'
            else:
                self.show_error("Registration failed")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")


class PasswordResetScreen(Screen):
    """Password reset screen with email verification."""
    reset_email_input = ObjectProperty(None)

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

    def on_reset_submit(self):
        """Handle password reset submission."""
        email = self.reset_email_input.text if self.reset_email_input else ""
        
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
        if self.reset_email_input:
            self.reset_email_input.text = ""

    def on_back_pressed(self):
        """Navigate back to login."""
        self.manager.current = 'login'
        if self.reset_email_input:
            self.reset_email_input.text = ""


class DashboardScreen(Screen):
    """User dashboard after successful authentication."""
    pass


class BankApp(App):
    """ArdenBank application main class."""
    current_user = None

    def build(self):
        return Builder.load_file('Screens/main.kv')


if __name__ == "__main__":
    BankApp().run()
