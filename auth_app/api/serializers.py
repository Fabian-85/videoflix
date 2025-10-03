from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'email': {
                'required': True
            }
        }

    def validate_confirmed_password(self, value):
        password = self.initial_data.get('password')
        if password and value and password != value:
            raise serializers.ValidationError('Passwords do not match')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def save(self):
        pw = self.validated_data['password']

        account = User(email=self.validated_data['email'], username=self.validated_data['email'], is_active=False)
        account.set_password(pw)
        account.save()
        return account
    

class CustomLoginSerializer(TokenObtainPairSerializer):
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if "username" in self.fields:
            self.fields.pop("username")
    
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except  User.DoesNotExist:
            raise serializers.ValidationError("No active account found with the given credentials")
        if not user.check_password(password):
             raise serializers.ValidationError("No active account found with the given credentials")
        data = super().validate({"username": user.username, "password":password})
        return data
    

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):

    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        pw1 = attrs.get("new_password")
        pw2 = attrs.get("confirm_password")
        print(pw1)
        print(pw2)
        if pw1 != pw2:
            raise serializers.ValidationError({"message": "passwords don't match!"})
        return attrs