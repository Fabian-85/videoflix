from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):

    """
    Serializer for registering a new user.

    Validates that the email is unique (case-sensitive) and saves the user as a inactive user with a hashed password,
    if password and confirmed_password are the same. The user is inactive.
    username is equal to email.
    """

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
        email = value.strip().lower() 
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Email already exists')
        return email

    def save(self):
        pw = self.validated_data['password']
        account = User(email=self.validated_data['email'], username=self.validated_data['email'], is_active=False)
        account.set_password(pw)
        account.save()
        return account
    

class CustomLoginSerializer(TokenObtainPairSerializer):

    """
    Custom Login Serializer with email and password
    """
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if "username" in self.fields:
            self.fields.pop("username")
    
    def validate(self, attrs):
        email = attrs.get("email").strip().lower()
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
    
    """
    Serializer for validate email adress (case-sensitive).
    """

    email = serializers.EmailField()

    def validate_email(self, value):
        email = value.strip().lower() 
        return email


class PasswordResetConfirmSerializer(serializers.Serializer):

    """
    Validates two matching new passwords in the reset confirmation step.

    Fields:
        new_password (write_only)
        confirm_password (write_only)
    """

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