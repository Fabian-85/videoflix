from django.urls import path
from .views import RegistrationView, ActivateAccountView, LoginView, RefreshTokenView, LogoutView, SendResetPasswordRequestView,PasswordResetConfirmView
 
urlpatterns = [
    path('register/', RegistrationView.as_view(), name='registration'),
    path("activate/<uidb64>/<token>/", ActivateAccountView.as_view(), name="activate_account"),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('password_reset/',  SendResetPasswordRequestView.as_view(), name='password_reset'),
    path('password_confirm/<uidb64>/<token>/',   PasswordResetConfirmView.as_view(), name='password_confirm'),
]