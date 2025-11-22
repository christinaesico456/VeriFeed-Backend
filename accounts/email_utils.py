from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)

def send_otp_email(user, otp_code, purpose='login'):
    """
    Send an OTP verification email using SendGrid with anti-spam optimizations.
    
    Args:
        user: CustomUser instance (must have .email and .username)
        otp_code: string or int - the OTP code
        purpose: 'login', 'signup', or 'reset'
    """
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Email, To, Content
        
        # Debug logging
        logger.info(f"🔍 Starting OTP email send for {user.email}, purpose: {purpose}")
        
        # Include OTP in subject (anti-spam best practice)
        subject_map = {
            'login': f'Your VeriFeed Login Code: {otp_code}',
            'signup': f'Welcome to VeriFeed - Verification Code: {otp_code}',
            'reset': f'VeriFeed Password Reset Code: {otp_code}',
        }
        subject = subject_map.get(purpose, f'VeriFeed Verification Code: {otp_code}')
        
        # Purpose-specific messaging
        purpose_messages = {
            'login': {
                'title': 'Login Verification',
                'greeting': f'Hello {user.username},',
                'message': 'You requested to log in to your VeriFeed account.',
                'action': 'Complete your login'
            },
            'signup': {
                'title': 'Welcome to VeriFeed!',
                'greeting': f'Welcome {user.username}!',
                'message': 'Thank you for creating a VeriFeed account. Please verify your email to get started.',
                'action': 'Verify your account'
            },
            'reset': {
                'title': 'Password Reset',
                'greeting': f'Hello {user.username},',
                'message': 'You requested to reset your VeriFeed password.',
                'action': 'Reset your password'
            }
        }
        
        purpose_info = purpose_messages.get(purpose, purpose_messages['login'])
        
        # Plain text version (important for spam filters)
        text_content = f"""
{purpose_info['greeting']}

{purpose_info['message']}

Your verification code is: {otp_code}

This code will expire in 5 minutes.

If you didn't request this code, please ignore this email or contact our support team at verifeedofficial@gmail.com.

Best regards,
The VeriFeed Team

---
VeriFeed - Deepfake Detection for Facebook
This is an automated message, please do not reply directly to this email.

To unsubscribe, email: verifeedofficial@gmail.com with subject "unsubscribe"
"""

        # Simplified HTML (less likely to trigger spam filters)
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, Helvetica, sans-serif; background-color: #ffffff;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width: 600px;">
                    
                    <!-- Header -->
                    <tr>
                        <td style="padding: 30px 20px; text-align: center; background-color: #4f46e5;">
                            <h1 style="margin: 0; font-size: 28px; color: #ffffff; font-weight: 600;">VeriFeed</h1>
                            <p style="margin: 8px 0 0 0; font-size: 14px; color: #e0e7ff;">{purpose_info['title']}</p>
                        </td>
                    </tr>
                    
                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px 30px; background-color: #ffffff; border-left: 1px solid #e5e7eb; border-right: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 20px 0; font-size: 16px; color: #111827; font-weight: 500;">{purpose_info['greeting']}</p>
                            <p style="margin: 0 0 30px 0; font-size: 14px; color: #4b5563; line-height: 1.6;">{purpose_info['message']}</p>
                            
                            <!-- OTP Box -->
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin: 0 0 30px 0;">
                                <tr>
                                    <td style="padding: 25px 20px; text-align: center; background-color: #f9fafb; border: 2px solid #d1d5db; border-radius: 8px;">
                                        <p style="margin: 0 0 12px 0; font-size: 11px; color: #6b7280; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Your Verification Code</p>
                                        <p style="margin: 0; font-size: 36px; font-weight: bold; color: #1f2937; letter-spacing: 8px; font-family: 'Courier New', Courier, monospace;">{otp_code}</p>
                                        <p style="margin: 12px 0 0 0; font-size: 13px; color: #6b7280;">Valid for 5 minutes</p>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Security Notice -->
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin: 0 0 20px 0;">
                                <tr>
                                    <td style="padding: 15px; background-color: #fef3c7; border-left: 3px solid #f59e0b; border-radius: 4px;">
                                        <p style="margin: 0; font-size: 13px; color: #92400e; line-height: 1.5;">
                                            <strong>Security Notice:</strong> Never share this code with anyone. VeriFeed will never ask for your verification code.
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 0; font-size: 13px; color: #6b7280; line-height: 1.5;">
                                If you didn't request this code, please ignore this email or contact us at 
                                <a href="mailto:verifeedofficial@gmail.com" style="color: #4f46e5; text-decoration: none;">verifeedofficial@gmail.com</a>
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 25px 30px; text-align: center; background-color: #f9fafb; border: 1px solid #e5e7eb; border-top: none;">
                            <p style="margin: 0 0 5px 0; font-size: 13px; color: #374151; font-weight: 600;">VeriFeed</p>
                            <p style="margin: 0 0 15px 0; font-size: 12px; color: #6b7280;">Deepfake Detection for Facebook</p>
                            <p style="margin: 0; font-size: 11px; color: #9ca3af;">
                                © 2025 VeriFeed. All rights reserved.
                            </p>
                            <p style="margin: 10px 0 0 0; font-size: 10px; color: #9ca3af;">
                                This is an automated message. Please do not reply.
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
        
        # Create message
        message = Mail(
            from_email=Email('verifeedofficial@gmail.com', 'VeriFeed Security'),
            to_emails=To(user.email),
            subject=subject,
            plain_text_content=Content("text/plain", text_content),
            html_content=Content("text/html", html_content)
        )
        
        # Add reply-to email
        message.reply_to = Email('verifeedofficial@gmail.com', 'VeriFeed Support')
        
        # Get API key from EMAIL_HOST_PASSWORD (Railway variable)
        api_key = os.environ.get('EMAIL_HOST_PASSWORD')
        if not api_key:
            logger.error("EMAIL_HOST_PASSWORD (SendGrid API key) not found in environment variables")
            return False
            
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        logger.info(f"✅ OTP email sent via SendGrid to {user.email} (status: {response.status_code})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send OTP email via SendGrid to {user.email}: {str(e)}")
        return False


def send_otp_success_notification(user, purpose='login'):
    """
    Notify user that OTP verification was successful.
    
    Args:
        user: CustomUser instance
        purpose: 'login' or 'signup'
    """
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Email, To, Content
        
        subject = 'VeriFeed - Login Successful' if purpose == 'login' else 'VeriFeed - Account Activated'
        
        text_content = f"""
Hello {user.username},

Your account was successfully {'accessed' if purpose == 'login' else 'verified and activated'}.

If this wasn't you, please secure your account immediately by:
1. Changing your password
2. Enabling two-factor authentication
3. Contacting our support team at verifeedofficial@gmail.com

Best regards,
The VeriFeed Team

---
VeriFeed - Deepfake Detection for Facebook
© 2025 VeriFeed. All rights reserved.

To unsubscribe, email: verifeedofficial@gmail.com with subject "unsubscribe"
"""
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, Helvetica, sans-serif; background-color: #ffffff;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table role="presentation" width="600" cellspacing="0" cellpadding="0" border="0" style="max-width: 600px; border: 1px solid #e5e7eb;">
                    
                    <!-- Header -->
                    <tr>
                        <td style="padding: 30px 20px; text-align: center; background-color: #4f46e5;">
                            <h1 style="margin: 0; font-size: 28px; color: #ffffff; font-weight: 600;">VeriFeed</h1>
                        </td>
                    </tr>
                    
                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px 30px; text-align: center; background-color: #ffffff;">
                            <!-- Success Icon -->
                            <div style="display: inline-block; width: 60px; height: 60px; background-color: #10b981; border-radius: 50%; margin-bottom: 20px; line-height: 60px; text-align: center;">
                                <span style="color: #ffffff; font-size: 32px; font-weight: bold;">✓</span>
                            </div>
                            
                            <h2 style="margin: 0 0 15px 0; color: #111827; font-size: 22px; font-weight: 600;">
                                {'Login Successful' if purpose == 'login' else 'Account Activated'}
                            </h2>
                            
                            <p style="margin: 0 0 30px 0; color: #4b5563; font-size: 14px; line-height: 1.6;">
                                Hello <strong style="color: #111827;">{user.username}</strong>, your account was successfully {'accessed' if purpose == 'login' else 'verified and activated'}.
                            </p>
                            
                            <!-- Info box -->
                            <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                                <tr>
                                    <td style="padding: 15px; background-color: #eff6ff; border-left: 3px solid #3b82f6; border-radius: 4px; text-align: left;">
                                        <p style="margin: 0; color: #1e40af; font-size: 13px; line-height: 1.5;">
                                            If this wasn't you, please contact us immediately at
                                            <a href="mailto:verifeedofficial@gmail.com" style="color: #1e40af; text-decoration: none; font-weight: 600;">verifeedofficial@gmail.com</a>
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 25px 30px; text-align: center; background-color: #f9fafb; border-top: 1px solid #e5e7eb;">
                            <p style="margin: 0 0 5px 0; font-size: 13px; color: #374151; font-weight: 600;">VeriFeed</p>
                            <p style="margin: 0 0 10px 0; font-size: 12px; color: #6b7280;">Deepfake Detection for Facebook</p>
                            <p style="margin: 0; font-size: 11px; color: #9ca3af;">© 2025 VeriFeed. All rights reserved.</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
        
        message = Mail(
            from_email=Email('verifeedofficial@gmail.com', 'VeriFeed Security'),
            to_emails=To(user.email),
            subject=subject,
            plain_text_content=Content("text/plain", text_content),
            html_content=Content("text/html", html_content)
        )
        
        message.reply_to = Email('verifeedofficial@gmail.com', 'VeriFeed Support')
        
        api_key = os.environ.get('EMAIL_HOST_PASSWORD')
        if not api_key:
            logger.error("EMAIL_HOST_PASSWORD not found")
            return False
            
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        logger.info(f"✅ Success notification sent to {user.email} (status: {response.status_code})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send success notification to {user.email}: {str(e)}")
        return False