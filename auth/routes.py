from app import app
from views import LoginView, RefreshTokenView, RegistrationView, RotationKeyView

app.add_url_rule('/login', view_func=LoginView.as_view('login'))
app.add_url_rule('/register', view_func=RegistrationView.as_view('register'))
app.add_url_rule('/keys', view_func=RotationKeyView.as_view('keys'))
app.add_url_rule('/refresh', view_func=RefreshTokenView.as_view('refresh'))