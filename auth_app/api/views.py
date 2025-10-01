from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .serializers import RegistrationSerializer
from .tokens import account_activation_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from django.contrib.auth import get_user_model


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
                    'uidb64':activate_url
                },
                'token':token
            }

            return Response(data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivateAccountView(APIView):
    dpermission_classes=[AllowAny]

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


class TestView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {'message': 'This is a Token test view!'}
        return Response(content)
