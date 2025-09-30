from django.urls import path
from .views import RegistrationView, TestView
 
urlpatterns = [
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('token-test/', TestView.as_view(), name='test')   
]