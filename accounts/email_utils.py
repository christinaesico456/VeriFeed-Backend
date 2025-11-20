from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)

def send_otp_email(user, otp_code, purpose='login'):
    """
    Send an OTP verification email using SendGrid.
    """
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Email, To, Content
        
        purpose_messages = {
            'login': {
                'title': 'Login Verification',
                'greeting': f'Hello {user.username},',
                'message': 'You requested to log in to your VeriFeed account.'
            },
            'signup': {
                'title': 'Welcome to VeriFeed!',
                'greeting': f'Welcome {user.username}!',
                'message': 'Thank you for creating a VeriFeed account.'
            },
            'reset': {
                'title': 'Password Reset',
                'greeting': f'Hello {user.username},',
                'message': 'You requested to reset your VeriFeed password.'
            }
        }
        
        purpose_info = purpose_messages.get(purpose, purpose_messages['login'])
        subject = f'VeriFeed - {purpose_info["title"]} Code: {otp_code}'
        
        text_content = f"""
{purpose_info['greeting']}

{purpose_info['message']}

Your verification code is: {otp_code}

This code will expire in 5 minutes.

Best regards,
The VeriFeed Team
"""

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{subject}</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; padding: 40px;">
        <h1 style="color: #333; text-align: center;">VeriFeed</h1>
        <h2 style="color: #666;">{purpose_info['title']}</h2>
        <p>{purpose_info['greeting']}</p>
        <p>{purpose_info['message']}</p>
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; text-align: center; margin: 30px 0;">
            <p style="color: white; margin: 0 0 10px 0;">YOUR VERIFICATION CODE</p>
            <p style="color: white; font-size: 36px; font-weight: bold; letter-spacing: 5px; margin: 0;">{otp_code}</p>
        </div>
        <p style="color: #999; font-size: 12px;">This code expires in 5 minutes.</p>
        <p style="color: #999; font-size: 12px;">© 2025 VeriFeed. All rights reserved.</p>
    </div>
</body>
</html>
"""
        
        message = Mail(
            from_email=Email('verifeedofficial@gmail.com', 'VeriFeed'),
            to_emails=To(user.email),
            subject=subject,
            plain_text_content=Content("text/plain", text_content),
            html_content=Content("text/html", html_content)
        )
        
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        
        logger.info(f"✅ OTP sent via SendGrid to {user.email} (status: {response.status_code})")
        return True
        
    except Exception as e:
        logger.error(f"❌ SendGrid error for {user.email}: {str(e)}")
        return False


def send_otp_success_notification(user, purpose='login'):
    """Optional success notification"""
    return True