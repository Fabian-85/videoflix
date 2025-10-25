from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .tokens import account_activation_token
from .serializers import RegistrationSerializer, CustomLoginSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView)
from rest_framework_simplejwt.tokens import RefreshToken
from .signals_def import password_reset_requested, email_verification_requested

User = get_user_model()

class RegistrationView(APIView):

    """
    View for user registration.    

    Permissions:
        AllowAny: Anyone can register.

    POST:
        Receives: JSON with 'email', 'password'
        email must be unique.
        Creates a new user and returns a success message or error details.
        Send an activation email to activate the currently inactive user.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()
            token = account_activation_token.make_token(saved_account)
            data = {
                'user': {
                    'user_id': saved_account.pk,
                    'email': saved_account.email,
                },
                'token':token
            }
            email_verification_requested.send(sender=self.__class__,user=saved_account ,email=saved_account.email,token=token, request=request)
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateAccountView(APIView):

    """
    View to activate a user account via token.

    Permissions:
        AllowAny: Anyone with a valid link can activate.

    GET:
        Path params: 'uidb64', 'token'
        Validates the token for the given user.
        On success: sets 'is_active=True' and returns 200.
        On failure: returns 400 with an error message.
    """

    permission_classes=[AllowAny]

    def get(self, request, uidb64, token):
        try:
         uid = force_str(urlsafe_base64_decode(uidb64))
         user = User.objects.get(pk=uid)
        except:
            return Response({"message": "User not found"},status=status.HTTP_400_BAD_REQUEST)
        is_token_valid = account_activation_token.check_token(user, token)
        if is_token_valid:
            user.is_active = True
            user.save()
            return Response({"message": "Account successfully activated"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Token is inactive or user does not match with this token"},status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):

    """
    View for user login.

    Permissions:
        AllowAny: Anyone can attempt to log in.

    POST:
        Receives: JSON with 'username' and 'password'.
        Returns: Sets 'access' and 'refresh' tokens in HttpOnly cookies and returns user details on successful authentication.
    """

    serializer_class = CustomLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh = serializer.validated_data["refresh"] 
        access = serializer.validated_data["access"]
        
        response = Response({"detail":"Login successful","user":{"id":serializer.user.id,"username":serializer.user.username}},status=status.HTTP_200_OK)
        response.set_cookie("refresh_token", value=refresh,httponly=True,secure=True,samesite="Lax")
        response.set_cookie("access_token", value=access,httponly=True,secure=True,samesite="Lax")
        return response

class RefreshTokenView(TokenRefreshView):

    """
    View for refreshing JWT access tokens.

    Permissions:
        AllowAny: Anyone can attempt to refresh the token.

    POST:
        Receives: No body required, uses 'refresh_token' from HttpOnly cookie.
        Returns: Sets a new 'access' token in an HttpOnly cookie and returns a success message.

    """

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response({"detail":"Refreshed Token is missing"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.get_serializer(data={"refresh":refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except:
            return Response({"detail":"Refresh Token is invalid!"}, status=status.HTTP_401_UNAUTHORIZED)
        access_token = serializer.validated_data.get("access")
        response = Response({"detail":"Token refreshed","access":access_token}, status=status.HTTP_200_OK)
        response.set_cookie("access_token", value=access_token,httponly=True,secure=True,samesite="Lax")
        return response
    

class LogoutView(APIView):

    """
    View for user logout.
    
    Permissions:
        IsAuthenticated: Only authenticated users can log out.

    POST:
        Receives: No body required, uses token from HttpOnly cookie.
        Returns: Blacklists the refresh token, deletes 'access' and 'refresh' cookies, and returns a success message.
    
    """
    
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token is None:
            return Response({"detail": "Refresh token not provided."},status=status.HTTP_400_BAD_REQUEST )
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except:
            return Response({"detail": "Invalid Refresh Token."}, status=status.HTTP_400_BAD_REQUEST)

        response = Response({"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."}, status=status.HTTP_200_OK)
        response.delete_cookie('refresh_token')
        response.delete_cookie('access_token')
        return response
    
class SendResetPasswordRequestView(APIView):

    """
    View to start the password reset flow.

    Permissions:
        AllowAny: Anyone can request a reset with an email address.

    POST:
        Receives: JSON with 'email'.
        If a matching user exists, emits a signal to send a reset email asynchronously.
        Always returns a generic 200 response to avoid account enumeration.
    """

    permission_classes = [AllowAny]

    def post(self,request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()
        if user and user.email:
            password_reset_requested.send(sender=self.__class__, user=user, request=request)
        return Response({"detail": "If account exists, then the email will be sent."}, status=status.HTTP_200_OK)
        

class PasswordResetConfirmView(APIView):

    """
    View to set a new password using uid/token.

    Permissions:
        AllowAny: Anyone with a valid link can complete the reset.

    POST:
        Path params: 'uidb64', 'token'.
        Receives: JSON with 'new_password', 'confirm_password'.
        Validates the reset token and matching passwords, then updates the user's password.
        On success: returns 200 with a success message.
        On failure: returns 400 with an error message.
    """

    permission_classes = [AllowAny]

    def post(self,request,uidb64, token):
        try:
         uid = force_str(urlsafe_base64_decode(uidb64))
         user = User.objects.get(pk=uid)
        except:
            return Response({"message": "invalid Token or user id"},status=status.HTTP_400_BAD_REQUEST)
        is_token_valid = default_token_generator.check_token(user, token)
        if is_token_valid:
             serializer = PasswordResetConfirmSerializer(data=request.data)
             serializer.is_valid(raise_exception=True)
             new_password = serializer.validated_data["new_password"]

             user.set_password(new_password)
             user.save(update_fields=["password"])

             return Response({"detail": "Your Password has been succesfully reset."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "invalid Token or user id"},status=status.HTTP_400_BAD_REQUEST)