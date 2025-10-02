from django.urls import path
from .views import RegistrationView, ActivateAccountView, LoginView, RefreshTokenView

 
urlpatterns = [
    path('register/', RegistrationView.as_view(), name='registration'),
    path("activate/<uidb64>/<token>/", ActivateAccountView.as_view(), name="activate_account"),
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('logout/', LoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),

]