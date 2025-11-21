from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)

def send_otp_email(user, otp_code, purpose='login'):
    """
    Send an OTP verification email using SendGrid with spam prevention.
    """
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Email, To, Content, Header
        
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
        
        # ✅ Remove OTP from subject line (spam trigger)
        subject_map = {
            'login': 'VeriFeed Login Verification',
            'signup': 'Welcome to VeriFeed - Verify Your Email',
            'reset': 'VeriFeed Password Reset Request',
        }
        subject = subject_map.get(purpose, 'VeriFeed Security Verification')
        
        # ✅Improved plain text version (must closely match HTML)
        text_content = f"""
{purpose_info['greeting']}

{purpose_info['message']}

Your verification code is: {otp_code}

This code will expire in 5 minutes. Please do not share this code with anyone.

If you did not request this code, please ignore this email or contact our support team.

Best regards,
The VeriFeed Team

Contact: verifeedofficial@gmail.com
VeriFeed - Deepfake Detection for Facebook

This is an automated security message. Please do not reply to this email.
"""

        #  Spam-optimized HTML (removed excessive gradients, emojis)
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, Helvetica, sans-serif; background-color: #f4f4f4;">
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #f4f4f4;">
        <tr>
            <td style="padding: 20px 10px;">
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" style="margin: 0 auto; background-color: #ffffff; border: 1px solid #dddddd;">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background-color: #4F46E5; padding: 30px 40px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: bold;">
                                VeriFeed
                            </h1>
                            <p style="margin: 8px 0 0 0; color: #ffffff; font-size: 14px;">
                                {purpose_info['title']}
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px;">
                            <p style="margin: 0 0 10px 0; color: #333333; font-size: 16px; font-weight: bold;">
                                {purpose_info['greeting']}
                            </p>
                            
                            <p style="margin: 0 0 30px 0; color: #555555; font-size: 14px; line-height: 1.6;">
                                {purpose_info['message']}
                            </p>
                            
                            <!-- OTP Code Box -->
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin: 0 0 30px 0;">
                                <tr>
                                    <td style="padding: 20px; background-color: #F3F4F6; border: 2px solid #4F46E5; text-align: center;">
                                        <p style="margin: 0 0 10px 0; color: #666666; font-size: 12px; font-weight: bold; text-transform: uppercase;">
                                            Your Verification Code
                                        </p>
                                        <p style="margin: 0; color: #1F2937; font-size: 32px; font-weight: bold; letter-spacing: 8px; font-family: 'Courier New', monospace;">
                                            {otp_code}
                                        </p>
                                        <p style="margin: 10px 0 0 0; color: #666666; font-size: 12px;">
                                            Expires in 5 minutes
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Security Notice -->
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="margin: 0 0 20px 0;">
                                <tr>
                                    <td style="padding: 15px; background-color: #FEF3C7; border-left: 4px solid #F59E0B;">
                                        <p style="margin: 0; color: #92400E; font-size: 13px; line-height: 1.5;">
                                            <strong>Security Notice:</strong> Never share this code with anyone. VeriFeed staff will never ask for your verification code.
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 0; color: #666666; font-size: 13px; line-height: 1.6;">
                                If you did not request this code, please ignore this email or contact us at 
                                <a href="mailto:verifeedofficial@gmail.com" style="color: #4F46E5; text-decoration: none;">verifeedofficial@gmail.com</a>
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 20px 40px; background-color: #F9FAFB; border-top: 1px solid #E5E7EB; text-align: center;">
                            <p style="margin: 0 0 5px 0; color: #333333; font-size: 14px; font-weight: bold;">
                                VeriFeed
                            </p>
                            <p style="margin: 0 0 5px 0; color: #666666; font-size: 12px;">
                                Deepfake Detection for Facebook
                            </p>
                            <p style="margin: 0; color: #999999; font-size: 11px;">
                                Copyright 2025 VeriFeed. All rights reserved.
                            </p>
                        </td>
                    </tr>
                    
                </table>
                
                <!-- Disclaimer -->
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" style="margin: 15px auto 0 auto;">
                    <tr>
                        <td style="text-align: center; padding: 0 20px;">
                            <p style="margin: 0; color: #999999; font-size: 11px; line-height: 1.4;">
                                This is an automated security message. Please do not reply to this email.
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
        
        # Add proper email headers to improve deliverability
        message = Mail(
            from_email=Email('verifeedofficial@gmail.com', 'VeriFeed Security'),
            to_emails=To(user.email),
            subject=subject,
            plain_text_content=Content("text/plain", text_content),
            html_content=Content("text/html", html_content)
        )
        
        # Send via SendGrid
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        
        logger.info(f"✅ OTP email sent via SendGrid to {user.email} (status: {response.status_code})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send OTP email via SendGrid to {user.email}: {str(e)}")
        return False


def send_otp_success_notification(user, purpose='login'):
    """
    Notify user that OTP verification was successful.
    """
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Email, To, Content
        
        subject = 'VeriFeed Login Successful' if purpose == 'login' else 'VeriFeed Account Activated'
        
        text_content = f"""
Hello {user.username},

Your account was successfully {'accessed' if purpose == 'login' else 'verified and activated'}.

If this was not you, please secure your account immediately by contacting our support team.

Best regards,
The VeriFeed Team

Contact: verifeedofficial@gmail.com
VeriFeed - Deepfake Detection for Facebook
Copyright 2025 VeriFeed. All rights reserved.
"""
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, Helvetica, sans-serif; background-color: #f4f4f4;">
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #f4f4f4;">
        <tr>
            <td style="padding: 20px 10px;">
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" style="margin: 0 auto; background-color: #ffffff; border: 1px solid #dddddd;">
                    <!-- Header -->
                    <tr>
                        <td style="background-color: #4F46E5; padding: 30px 40px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: bold;">
                                VeriFeed
                            </h1>
                        </td>
                    </tr>
                    
                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px; text-align: center;">
                            <div style="width: 60px; height: 60px; background-color: #10B981; border-radius: 50%; margin: 0 auto 20px auto; display: flex; align-items: center; justify-content: center;">
                                <p style="margin: 0; color: #ffffff; font-size: 30px; line-height: 60px;">✓</p>
                            </div>
                            
                            <h2 style="margin: 0 0 15px 0; color: #1F2937; font-size: 22px; font-weight: bold;">
                                {'Login Successful' if purpose == 'login' else 'Account Activated'}
                            </h2>
                            
                            <p style="margin: 0 0 30px 0; color: #555555; font-size: 14px; line-height: 1.6;">
                                Hello <strong>{user.username}</strong>, your account was successfully {'accessed' if purpose == 'login' else 'verified and activated'}.
                            </p>
                            
                            <!-- Info box -->
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                <tr>
                                    <td style="padding: 15px; background-color: #EFF6FF; border-left: 4px solid #3B82F6; text-align: left;">
                                        <p style="margin: 0; color: #1F2937; font-size: 13px; line-height: 1.5;">
                                            If this was not you, please contact us immediately at 
                                            <a href="mailto:verifeedofficial@gmail.com" style="color: #4F46E5; text-decoration: none;">verifeedofficial@gmail.com</a>
                                        </p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 20px 40px; background-color: #F9FAFB; border-top: 1px solid #E5E7EB; text-align: center;">
                            <p style="margin: 0 0 5px 0; color: #333333; font-size: 14px; font-weight: bold;">
                                VeriFeed
                            </p>
                            <p style="margin: 0 0 5px 0; color: #666666; font-size: 12px;">
                                Deepfake Detection for Facebook
                            </p>
                            <p style="margin: 0; color: #999999; font-size: 11px;">
                                Copyright 2025 VeriFeed. All rights reserved.
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
        
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to send success notification to {user.email}: {str(e)}")
        return False