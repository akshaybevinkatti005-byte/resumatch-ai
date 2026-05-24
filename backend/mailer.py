"""
ResuMatch AI — Email Verification Mailer
Sends verification emails using Python's built-in smtplib (no third-party APIs).
Falls back to console output when SMTP credentials are not configured.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ──────── SMTP Configuration ────────
# Set these environment variables to enable real email delivery:
#   SMTP_HOST      — e.g. smtp.gmail.com
#   SMTP_PORT      — e.g. 587
#   SMTP_USER      — your email address
#   SMTP_PASSWORD  — your app password (not regular password)
#   FRONTEND_URL   — e.g. http://localhost:5173

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")


def _build_verification_url(token: str) -> str:
    """Build the verification URL that points to the backend verify endpoint."""
    return f"{BACKEND_URL}/auth/verify?token={token}"


def _build_html_email(name: str, verification_url: str) -> str:
    """Build a beautiful HTML verification email."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin:0;padding:0;background-color:#0f0f1a;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0f0f1a;padding:40px 20px;">
            <tr>
                <td align="center">
                    <table width="520" cellpadding="0" cellspacing="0" style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);border-radius:16px;overflow:hidden;border:1px solid rgba(99,102,241,0.2);">
                        <!-- Header -->
                        <tr>
                            <td style="padding:40px 40px 20px;text-align:center;">
                                <div style="font-size:32px;font-weight:700;background:linear-gradient(135deg,#818cf8,#a78bfa,#c084fc);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
                                    ResuMatch AI
                                </div>
                                <div style="color:#94a3b8;font-size:14px;margin-top:8px;">
                                    Zero-cost resume optimization
                                </div>
                            </td>
                        </tr>
                        <!-- Body -->
                        <tr>
                            <td style="padding:20px 40px;">
                                <h2 style="color:#e2e8f0;font-size:22px;margin:0 0 16px;">
                                    Verify your email address
                                </h2>
                                <p style="color:#94a3b8;font-size:15px;line-height:1.6;margin:0 0 24px;">
                                    Hi <strong style="color:#c4b5fd;">{name}</strong>,<br><br>
                                    Thanks for signing up! Click the button below to verify your email
                                    and start optimizing your resume with AI-powered insights.
                                </p>
                                <!-- CTA Button -->
                                <table width="100%" cellpadding="0" cellspacing="0">
                                    <tr>
                                        <td align="center" style="padding:8px 0 24px;">
                                            <a href="{verification_url}"
                                               style="display:inline-block;padding:14px 48px;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#ffffff;text-decoration:none;border-radius:10px;font-size:16px;font-weight:600;letter-spacing:0.5px;">
                                                Verify Email
                                            </a>
                                        </td>
                                    </tr>
                                </table>
                                <p style="color:#64748b;font-size:13px;line-height:1.5;margin:0 0 8px;">
                                    If the button doesn't work, copy and paste this link into your browser:
                                </p>
                                <p style="color:#818cf8;font-size:12px;word-break:break-all;margin:0 0 24px;padding:12px;background:rgba(99,102,241,0.1);border-radius:8px;">
                                    {verification_url}
                                </p>
                            </td>
                        </tr>
                        <!-- Footer -->
                        <tr>
                            <td style="padding:20px 40px 30px;border-top:1px solid rgba(99,102,241,0.15);">
                                <p style="color:#475569;font-size:12px;margin:0;text-align:center;">
                                    This link expires in 24 hours. If you didn't create an account, you can safely ignore this email.
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


def _build_plain_text_email(name: str, verification_url: str) -> str:
    """Build a plain text fallback for the verification email."""
    return (
        f"Hi {name},\n\n"
        f"Thanks for signing up for ResuMatch AI!\n\n"
        f"Please verify your email by clicking the link below:\n"
        f"{verification_url}\n\n"
        f"This link expires in 24 hours.\n\n"
        f"If you didn't create an account, you can safely ignore this email.\n\n"
        f"— ResuMatch AI"
    )


def send_verification_email(email: str, name: str, token: str) -> bool:
    """
    Send a verification email to the user.

    If SMTP credentials are configured, sends a real email.
    Otherwise, prints the verification link to the console for local testing.

    Returns:
        True if the email was sent (or printed) successfully, False otherwise.
    """
    verification_url = _build_verification_url(token)

    # ── Console Fallback (no SMTP configured) ──
    if not SMTP_USER or not SMTP_PASSWORD:
        print("\n" + "=" * 60)
        print("[MAILER] SMTP not configured — Console Fallback Mode")
        print(f"[MAILER] Verification email for: {email}")
        print(f"[MAILER] Click this link to verify:")
        print(f"[MAILER] {verification_url}")
        print("=" * 60 + "\n")
        return True

    # ── Real SMTP Email Delivery ──
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Verify your email — ResuMatch AI"
        msg["From"] = SMTP_USER
        msg["To"] = email

        # Attach both plain text and HTML versions
        plain_body = _build_plain_text_email(name, verification_url)
        html_body = _build_html_email(name, verification_url)

        msg.attach(MIMEText(plain_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, email, msg.as_string())

        print(f"[MAILER] Verification email sent to {email} [OK]")
        return True

    except smtplib.SMTPAuthenticationError:
        print(f"[MAILER] SMTP authentication failed. Check SMTP_USER and SMTP_PASSWORD.")
        # Fall back to console
        print(f"[MAILER] Falling back to console. Verification link: {verification_url}")
        return True

    except Exception as e:
        print(f"[MAILER] Failed to send email: {e}")
        # Fall back to console so user is never blocked
        print(f"[MAILER] Falling back to console. Verification link: {verification_url}")
        return True
