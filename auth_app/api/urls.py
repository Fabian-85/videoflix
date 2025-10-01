from django.urls import path
from .views import RegistrationView, ActivateAccountView, TestView
 
urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path("activate/<uidb64>/<token>/", ActivateAccountView.as_view(), name="activate_account"),
    path('token-test/', TestView.as_view(), name='test')   
]