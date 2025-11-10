from rest_framework import serializers
from .models import UserOTP, CustomUser
from django.utils import timezone


class RequestOTPSerializer(serializers.Serializer):
    """Serializer for requesting OTP code"""
    username_or_email = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    purpose = serializers.ChoiceField(
        choices=['login', 'signup'],
        default='login'
    )

    def validate(self, data):
        username_or_email = data.get('username_or_email')
        password = data.get('password')
        purpose = data.get('purpose')

        # Find user by email or username
        user = None
        if '@' in username_or_email:
            try:
                user = CustomUser.objects.get(email=username_or_email)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError("Invalid credentials")
        else:
            try:
                user = CustomUser.objects.get(username=username_or_email)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError("Invalid credentials")

        # Verify password
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials")

        # Check if 2FA is enabled
        if not user.two_fa_enabled and purpose == 'login':
            raise serializers.ValidationError(
                "2FA is not enabled for this account"
            )

        data['user'] = user
        return data


class VerifyOTPSerializer(serializers.Serializer):
    """Serializer for verifying OTP code"""
    username_or_email = serializers.CharField(required=True)
    otp_code = serializers.CharField(required=True, min_length=6, max_length=6)
    purpose = serializers.ChoiceField(
        choices=['login', 'signup'],
        default='login'
    )

    def validate_otp_code(self, value):
        """Validate OTP code format"""
        if not value.isdigit():
            raise serializers.ValidationError("OTP must contain only digits")
        return value

    def validate(self, data):
        username_or_email = data.get('username_or_email')
        otp_code = data.get('otp_code')
        purpose = data.get('purpose')

        # Find user
        user = None
        if '@' in username_or_email:
            try:
                user = CustomUser.objects.get(email=username_or_email)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError("Invalid user")
        else:
            try:
                user = CustomUser.objects.get(username=username_or_email)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError("Invalid user")

        # Find the latest valid OTP for this user and purpose
        otp = UserOTP.objects.filter(
            user=user,
            purpose=purpose,
            is_used=False,
            expires_at__gt=timezone.now()
        ).order_by('-created_at').first()

        if not otp:
            raise serializers.ValidationError(
                "No valid OTP found. Please request a new one."
            )

        # Check if OTP is locked due to too many failed attempts
        if otp.failed_attempts >= 5:
            raise serializers.ValidationError(
                "Too many failed attempts. Please request a new OTP."
            )

        # Verify the OTP code
        if not otp.verify(otp_code):
            remaining_attempts = 5 - (otp.failed_attempts)
            raise serializers.ValidationError(
                f"Invalid OTP code. {remaining_attempts} attempts remaining."
            )

        data['user'] = user
        data['otp'] = otp
        return data


class ResendOTPSerializer(serializers.Serializer):
    """Serializer for resending OTP"""
    username_or_email = serializers.CharField(required=True)
    purpose = serializers.ChoiceField(
        choices=['login', 'signup'],
        default='login'
    )

    def validate(self, data):
        username_or_email = data.get('username_or_email')

        # Find user
        user = None
        if '@' in username_or_email:
            try:
                user = CustomUser.objects.get(email=username_or_email)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError("User not found")
        else:
            try:
                user = CustomUser.objects.get(username=username_or_email)
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError("User not found")

        data['user'] = user
        return data