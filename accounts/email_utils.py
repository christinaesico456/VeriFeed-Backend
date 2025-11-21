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
"""

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; background-color: #f8fafc;">
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #f8fafc;">
        <tr>
            <td style="padding: 40px 20px;">
                <!-- Main container -->
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" style="margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                    
                    <!-- Header with gradient -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #ec4899 100%); padding: 36px 40px; text-align: center; border-radius: 12px 12px 0 0;">
                            <h1 style="margin: 0 0 12px 0; color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;">
                                VeriFeed
                            </h1>
                            <div style="display: inline-block; padding: 6px 16px; background-color: rgba(255,255,255,0.25); border-radius: 16px;">
                                <p style="margin: 0; color: #ffffff; font-size: 14px; font-weight: 600;">
                                    🔒 {purpose_info['title']}
                                </p>
                            </div>
                        </td>
                    </tr>
                    
                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px 40px 32px 40px;">
                            <p style="margin: 0 0 8px 0; color: #111827; font-size: 18px; line-height: 26px; font-weight: 600;">
                                {purpose_info['greeting']}
                            </p>
                            
                            <p style="margin: 0 0 32px 0; color: #6b7280; font-size: 15px; line-height: 22px;">
                                {purpose_info['message']}
                            </p>
                            
                            <!-- OTP Code Box -->
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin: 0 0 32px 0;">
                                <tr>
                                    <td style="padding: 28px 24px; background: linear-gradient(135deg, #f0f9ff 0%, #faf5ff 50%, #fdf2f8 100%); border: 2px solid; border-image: linear-gradient(135deg, #60a5fa, #a78bfa, #ec4899) 1; border-radius: 10px; text-align: center;">
                                        <p style="margin: 0 0 12px 0; color: #9ca3af; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px;">
                                            YOUR VERIFICATION CODE
                                        </p>
                                        <p style="margin: 0; color: #1f2937; font-size: 40px; font-weight: 700; letter-spacing: 10px; font-family: 'Courier New', Consolas, monospace;">
                                            {otp_code}
                                        </p>
                                        <p style="margin: 12px 0 0 0; color: #9ca3af; font-size: 13px;">
                                            Expires in <span style="color: #6b7280; font-weight: 600;">5 minutes</span>
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Security Notice -->
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin: 0 0 24px 0;">
                                <tr>
                                    <td style="padding: 14px 16px; background-color: #fef3c7; border-left: 3px solid #f59e0b; border-radius: 6px;">
                                        <p style="margin: 0; color: #92400e; font-size: 13px; line-height: 18px;">
                                            <strong>⚠️ Security Notice:</strong> Never share this code with anyone. VeriFeed staff will never ask for your verification code.
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 0; color: #6b7280; font-size: 14px; line-height: 20px;">
                                If you didn't request this code, please ignore this email or contact us at
                                <a href="mailto:verifeedofficial@gmail.com" style="color: #a78bfa; text-decoration: none; font-weight: 600;">verifeedofficial@gmail.com</a>
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 24px 40px; background-color: #f9fafb; border-top: 1px solid #e5e7eb; border-radius: 0 0 12px 12px; text-align: center;">
                            <p style="margin: 0 0 6px 0; color: #374151; font-size: 13px; font-weight: 600;">
                                VeriFeed
                            </p>
                            <p style="margin: 0 0 4px 0; color: #6b7280; font-size: 12px;">
                                Deepfake Detection for Facebook
                            </p>
                            <p style="margin: 0; color: #9ca3af; font-size: 11px;">
                                © 2025 VeriFeed. All rights reserved.
                            </p>
                        </td>
                    </tr>
                    
                </table>
                
                <!-- Small disclaimer -->
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" style="margin: 16px auto 0 auto;">
                    <tr>
                        <td style="text-align: center; padding: 0 20px;">
                            <p style="margin: 0; color: #9ca3af; font-size: 11px; line-height: 16px;">
                                This is an automated message, please do not reply directly to this email.
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
        
        message = Mail(
            from_email=Email('verifeedofficial@gmail.com', 'VeriFeed Security'),
            to_emails=To(user.email),
            subject=subject,
            plain_text_content=Content("text/plain", text_content),
            html_content=Content("text/html", html_content)
        )
        
        # Add custom headers for spam prevention (SendGrid format)
        message.add_header('X-Entity-Ref-ID', f'verifeed-otp-{purpose}-{user.id}')
        message.add_header('X-Priority', '1')
        message.add_header('Importance', 'high')
        
        # Get API key
        api_key = os.environ.get('SENDGRID_API_KEY')
        if not api_key:
            logger.error("SENDGRID_API_KEY not found in environment variables")
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
"""
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; background-color: #f8fafc;">
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #f8fafc;">
        <tr>
            <td style="padding: 40px 20px;">
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" style="margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.08);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #ec4899 100%); padding: 36px 40px; text-align: center; border-radius: 12px 12px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 700; letter-spacing: -0.5px;">
                                VeriFeed
                            </h1>
                        </td>
                    </tr>
                    
                    <!-- Body -->
                    <tr>
                        <td style="padding: 48px 40px; text-align: center;">
                            <!-- Success Icon -->
                            <div style="display: inline-block; width: 64px; height: 64px; background-color: #10b981; border-radius: 50%; margin-bottom: 20px;">
                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" height="100%">
                                    <tr>
                                        <td style="text-align: center; vertical-align: middle;">
                                            <span style="color: #ffffff; font-size: 32px; font-weight: bold;">✓</span>
                                        </td>
                                    </tr>
                                </table>
                            </div>
                            
                            <h2 style="margin: 0 0 12px 0; color: #111827; font-size: 24px; font-weight: 700;">
                                {'Login Successful' if purpose == 'login' else 'Account Activated'}
                            </h2>
                            
                            <p style="margin: 0 0 32px 0; color: #6b7280; font-size: 15px; line-height: 22px;">
                                Hello <strong style="color: #374151;">{user.username}</strong>, your account was successfully {'accessed' if purpose == 'login' else 'verified and activated'}.
                            </p>
                            
                            <!-- Info box -->
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td style="padding: 14px 16px; background-color: #eff6ff; border-left: 3px solid #60a5fa; border-radius: 6px; text-align: left;">
                                        <p style="margin: 0; color: #6b7280; font-size: 13px; line-height: 18px;">
                                            If this wasn't you, please contact us immediately at
                                            <a href="mailto:verifeedofficial@gmail.com" style="color: #a78bfa; text-decoration: none; font-weight: 600;">verifeedofficial@gmail.com</a>
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 24px 40px; background-color: #f9fafb; border-top: 1px solid #e5e7eb; border-radius: 0 0 12px 12px; text-align: center;">
                            <p style="margin: 0 0 6px 0; color: #374151; font-size: 13px; font-weight: 600;">
                                VeriFeed
                            </p>
                            <p style="margin: 0 0 4px 0; color: #6b7280; font-size: 12px;">
                                Deepfake Detection for Facebook
                            </p>
                            <p style="margin: 0; color: #9ca3af; font-size: 11px;">
                                © 2025 VeriFeed. All rights reserved.
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
        
        message = Mail(
            from_email=Email('verifeedofficial@gmail.com', 'VeriFeed Security'),
            to_emails=To(user.email),
            subject=subject,
            plain_text_content=Content("text/plain", text_content),
            html_content=Content("text/html", html_content)
        )
        
        api_key = os.environ.get('SENDGRID_API_KEY')
        if not api_key:
            logger.error("SENDGRID_API_KEY not found in environment variables")
            return False
            
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        logger.info(f"✅ Success notification sent to {user.email} (status: {response.status_code})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send success notification to {user.email}: {str(e)}")
        return False