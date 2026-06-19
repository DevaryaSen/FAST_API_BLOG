import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import settings


async def send_password_reset_email(to_email: str, username: str, token: str) -> None:
    reset_url = f"{settings.frontend_url}/reset-password?token={token}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Password Reset Request"
    msg["From"] = settings.mail_from
    msg["To"] = to_email

    text_body = f"""Hi {username},

You requested a password reset. Use the link below to reset your password:

{reset_url}

This link expires in {settings.reset_token_expire_minutes} minutes.

If you did not request this, please ignore this email.
"""

    html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
  <h2>Password Reset Request</h2>
  <p>Hi {username},</p>
  <p>You requested a password reset. Click the button below to reset your password:</p>
  <p>
    <a href="{reset_url}"
       style="background:#000;color:#fff;padding:10px 20px;text-decoration:none;display:inline-block;">
      Reset Password
    </a>
  </p>
  <p>This link expires in {settings.reset_token_expire_minutes} minutes.</p>
  <p>If you did not request this, please ignore this email.</p>
</body>
</html>
"""

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.mail_server,
            port=settings.mail_port,
            username=settings.mail_username or None,
            password=settings.mail_password.get_secret_value() or None,
            use_tls=False,
            start_tls=settings.mail_use_tls,
        )
    except Exception as e:
        # Log but don't raise — we don't want to leak whether email exists
        print(f"Failed to send password reset email: {e}")
