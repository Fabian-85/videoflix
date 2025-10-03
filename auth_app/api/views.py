from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.tokens import default_token_generator
from .serializers import RegistrationSerializer, CustomLoginSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from .tokens import account_activation_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView)
from rest_framework_simplejwt.tokens import RefreshToken
from .signals_def import password_reset_requested

User = get_user_model()

class RegistrationView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        data = {}
        if serializer.is_valid():
            saved_account = serializer.save()
            uidb64 = urlsafe_base64_encode(force_bytes(saved_account.pk))
            token = account_activation_token.make_token(saved_account)
            activate_path = reverse("activate_account", kwargs={"uidb64": uidb64, "token": token})
            activate_url = request.build_absolute_uri(activate_path)
            data = {
                'user': {
                    'user_id': saved_account.pk,
                    'email': saved_account.email,
                    'url':activate_url
                },
                'token':token
            }

            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateAccountView(APIView):
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
            print("True")
            return Response({"message": "Account successfully activated"})
        else:
            return Response({"message": "User Account is active"})


class LoginView(TokenObtainPairView):

    serializer_class = CustomLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh = serializer.validated_data["refresh"] 
        access = serializer.validated_data["access"]
        
        response = Response({"detail":"Login successful","user":{"id":serializer.user.id,"username":serializer.user.username}})
        response.set_cookie("refresh_token", value=refresh,httponly=True,secure=True,samesite="Lax")
        response.set_cookie("access_token", value=access,httponly=True,secure=True,samesite="Lax")
        return response

class RefreshTokenView(TokenRefreshView):
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
        response = Response({"detail":"Token refreshed","acess":access_token}, status=status.HTTP_200_OK)
        response.set_cookie("access_token", value=access_token,httponly=True,secure=True,samesite="Lax")
        return response
    

class LogoutView(APIView):
    
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

    permission_classes = [AllowAny]

    def post(self,request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        print(email)
        user = User.objects.filter(email=email).first()
        if user and user.email:
            password_reset_requested.send(sender=self.__class__, user=user, request=request)
        return Response({"detail": "If account exists, then the email will be sent."}, status=status.HTTP_200_OK)
        

class PasswordResetConfirmView(APIView):

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
            return Response({"message": "invalid Token or user id"})