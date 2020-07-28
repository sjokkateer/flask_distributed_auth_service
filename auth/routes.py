from app import app
from views import LoginView, RefreshTokenView, RegistrationView, RotationKeyView, UserView

app.add_url_rule('/login', view_func=LoginView.as_view('login'))
app.add_url_rule('/register', view_func=RegistrationView.as_view('register'))
app.add_url_rule('/keys/<int:key_id>', view_func=RotationKeyView.as_view('keys'))
app.add_url_rule('/refresh', view_func=RefreshTokenView.as_view('refresh'))
app.add_url_rule('/users/<int:id>', view_func=UserView.as_view('users'))
