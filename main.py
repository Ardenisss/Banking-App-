# main.py
from kivy.app import App
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager

# import BEFORE loading KV so custom classes (HoverLabel, HoverButton) work
from hover import HoverLabel
from firebase_init import register_user, login_user

# Screen classes
class LoginScreen(Screen):
    username_input = ObjectProperty(None)
    password_input = ObjectProperty(None)
    login_btn = ObjectProperty(None)
    forgot_btn = ObjectProperty(None)
    register_btn = ObjectProperty(None)

    def on_login_pressed(self):
        email = self.username_input.text if self.username_input else ""
        pw = self.password_input.text if self.password_input else ""
        try:
            user = login_user(email, pw)  # your firebase login function
            if user:
                App.get_running_app().current_user = user  # store user in App
                print("Login successful:", user)
                self.manager.current = 'dashboard'  # switch to dashboard
            else:
                print("Login failed: check email/password")
        except Exception as e:
            print("Error during login:", e)


    def on_forgot_pressed(self):
        print("Forgot pressed")


class RegisterScreen(Screen):
    new_username_input = ObjectProperty(None)
    new_password_input = ObjectProperty(None)
    confirm_password_input = ObjectProperty(None)
    submit_btn = ObjectProperty(None)
    back_btn = ObjectProperty(None)

    def on_register_submit(self):
        email = self.new_username_input.text if self.new_username_input else ""
        pw = self.new_password_input.text if self.new_password_input else ""
        pwc = self.confirm_password_input.text if self.confirm_password_input else ""

        if not email or not pw or not pwc:
            print("Please fill all fields")
            return

        if pw != pwc:
            print("Passwords do not match")
            return

        try:
            user = register_user(email, pw)  # your firebase register function
            if user:
                App.get_running_app().current_user = user  # store user in App
                print("Registration successful:", user)
                self.manager.current = 'dashboard'  # switch to dashboard
            else:
                print("Registration failed")
        except Exception as e:
            print("Error during registration:", e)

class DashboardScreen(Screen):
    pass

# Build the app
class BankApp(App):
    current_user = None  # will hold the logged-in user info
    def build(self):
        return Builder.load_file('Screens/main.kv')


if __name__ == "__main__":
    BankApp().run()
