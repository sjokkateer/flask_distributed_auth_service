from app import app
from decorators import verify_token_and_user_resource_access
from views import LoginView, RefreshTokenView, RegistrationView, RotationKeyView, UserView

app.add_url_rule('/login', view_func=LoginView.as_view('login'))
app.add_url_rule('/register', view_func=RegistrationView.as_view('register'))
app.add_url_rule('/keys', view_func=RotationKeyView.as_view('keys'))
app.add_url_rule('/keys/<int:key_id>', view_func=RotationKeyView.as_view('key'))
app.add_url_rule('/refresh', view_func=RefreshTokenView.as_view('refresh'))

user_view = verify_token_and_user_resource_access(UserView.as_view('users'))
app.add_url_rule('/users/<int:id>', view_func=user_view)
