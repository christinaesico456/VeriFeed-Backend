from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserOTP
from .otp_serializers import (
    RequestOTPSerializer, 
    VerifyOTPSerializer,
    ResendOTPSerializer
)
from .email_utils import send_otp_email, send_otp_success_notification
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@api_view(['POST'])
@permission_classes([AllowAny])
def request_otp(request):
    """
    Step 1: Request OTP code
    User provides credentials, system sends OTP to their email
    """
    logger.info(f"OTP request received: {request.data.get('username_or_email')}")
    
    serializer = RequestOTPSerializer(data=request.data)
    
    if not serializer.is_valid():
        logger.error(f"OTP request validation failed: {serializer.errors}")
        return Response(
            {'error': 'Invalid credentials or data', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = serializer.validated_data['user']
    purpose = serializer.validated_data.get('purpose', 'login')
    ip_address = get_client_ip(request)
    
    try:
        # Generate OTP
        otp = UserOTP.generate_otp(user, purpose=purpose, ip_address=ip_address)
        
        # Send OTP via email
        email_sent = send_otp_email(user, otp.otp_code, purpose=purpose)
        
        if not email_sent:
            logger.error(f"Failed to send OTP email to {user.email}")
            return Response(
                {'error': 'Failed to send OTP email. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        logger.info(f"OTP generated and sent to {user.email}")
        
        return Response({
            'message': 'OTP sent successfully to your email',
            'email': f"{user.email[:3]}***{user.email.split('@')[1]}",  # Masked email
            'expires_in': 300,  # 5 minutes in seconds
            'requires_otp': True
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error generating OTP: {str(e)}")
        return Response(
            {'error': 'Failed to generate OTP. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    """
    Step 2: Verify OTP code
    User provides OTP, system validates and issues JWT token
    """
    logger.info(f"OTP verification attempt: {request.data.get('username_or_email')}")
    
    serializer = VerifyOTPSerializer(data=request.data)
    
    if not serializer.is_valid():
        logger.error(f"OTP verification failed: {serializer.errors}")
        return Response(
            {'error': 'Invalid OTP or data', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = serializer.validated_data['user']
    purpose = serializer.validated_data.get('purpose', 'login')
    
    try:
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Get profile picture URL
        profile_picture_url = None
        if user.profile_picture:
            profile_picture_url = request.build_absolute_uri(user.profile_picture.url)
        
        # Send success notification
        send_otp_success_notification(user, purpose=purpose)
        
        logger.info(f"OTP verified successfully for {user.username}")
        
        response_data = {
            'message': '2FA verification successful',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': f"{user.first_name} {user.last_name}".strip(),
                'profile_picture': profile_picture_url,
                'two_fa_enabled': user.two_fa_enabled
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error verifying OTP: {str(e)}")
        return Response(
            {'error': 'Verification failed. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_otp(request):
    """
    Resend OTP code to user's email
    """
    logger.info(f"OTP resend request: {request.data.get('username_or_email')}")
    
    serializer = ResendOTPSerializer(data=request.data)
    
    if not serializer.is_valid():
        logger.error(f"OTP resend validation failed: {serializer.errors}")
        return Response(
            {'error': 'Invalid data', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = serializer.validated_data['user']
    purpose = serializer.validated_data.get('purpose', 'login')
    ip_address = get_client_ip(request)
    
    try:
        # Generate new OTP
        otp = UserOTP.generate_otp(user, purpose=purpose, ip_address=ip_address)
        
        # Send OTP via email
        email_sent = send_otp_email(user, otp.otp_code, purpose=purpose)
        
        if not email_sent:
            return Response(
                {'error': 'Failed to send OTP email. Please try again.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        logger.info(f"OTP resent to {user.email}")
        
        return Response({
            'message': 'New OTP sent successfully',
            'expires_in': 300
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error resending OTP: {str(e)}")
        return Response(
            {'error': 'Failed to resend OTP. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def toggle_2fa(request):
    """
    Enable or disable 2FA for authenticated user
    Requires authentication
    """
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Authentication required'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    user = request.user
    enable = request.data.get('enable', True)
    
    user.two_fa_enabled = enable
    user.save()
    
    return Response({
        'message': f"2FA {'enabled' if enable else 'disabled'} successfully",
        'two_fa_enabled': user.two_fa_enabled
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def test_email(request):
    """Test endpoint to verify email configuration"""
    try:
        from django.core.mail import send_mail
        
        send_mail(
            'VeriFeed Test Email',
            'If you receive this, email configuration is working!',
            settings.DEFAULT_FROM_EMAIL,
            ['verifeedofficial@gmail.com'], 
            fail_silently=False,
        )
        
        return Response({
            'message': 'Test email sent successfully',
            'email_host': settings.EMAIL_HOST,
            'email_user': settings.EMAIL_HOST_USER,
            'email_port': settings.EMAIL_PORT,
        })
    except Exception as e:
        return Response({
            'error': str(e),
            'email_settings': {
                'host': settings.EMAIL_HOST,
                'port': settings.EMAIL_PORT,
                'user': settings.EMAIL_HOST_USER,
            }
        }, status=500)