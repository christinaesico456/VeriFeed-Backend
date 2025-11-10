from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
import random
import string

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        blank=True,
        null=True,
        default='profile_pics/default.jpg'
    )
    birthday = models.DateField(null=True, blank=True)
    two_fa_enabled = models.BooleanField(default=True)  # Enable 2FA by default

    def __str__(self):
        return self.username


class UserOTP(models.Model):
    """Store OTP codes for two-factor authentication"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otp_codes')
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=[
        ('login', 'Login'),
        ('signup', 'Signup'),
        ('reset', 'Password Reset'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    failed_attempts = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_used', 'expires_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.purpose} - {self.otp_code}"

    @classmethod
    def generate_otp(cls, user, purpose='login', ip_address=None):
        """Generate a new 6-digit OTP code"""
        # Invalidate any existing unused OTPs for this user and purpose
        cls.objects.filter(
            user=user,
            purpose=purpose,
            is_used=False
        ).update(is_used=True)

        # Generate random 6-digit code
        otp_code = ''.join(random.choices(string.digits, k=6))
        
        # Set expiration (5 minutes from now)
        expires_at = timezone.now() + timedelta(minutes=5)

        # Create new OTP
        otp = cls.objects.create(
            user=user,
            otp_code=otp_code,
            purpose=purpose,
            expires_at=expires_at,
            ip_address=ip_address
        )
        
        return otp

    def is_valid(self):
        """Check if OTP is still valid"""
        if self.is_used:
            return False
        if timezone.now() > self.expires_at:
            return False
        if self.failed_attempts >= 5:
            return False
        return True

    def verify(self, code):
        """Verify the OTP code"""
        if not self.is_valid():
            return False
        
        if self.otp_code == code:
            self.is_used = True
            self.save()
            return True
        else:
            self.failed_attempts += 1
            self.save()
            return False

    @property
    def time_remaining(self):
        """Get remaining time in seconds"""
        if timezone.now() > self.expires_at:
            return 0
        delta = self.expires_at - timezone.now()
        return int(delta.total_seconds())