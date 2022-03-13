import os, smtplib, ssl
import email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv


def send_email(subject, html_message, recipient_email, attachment_path=None):
    smtp_server = "smtp.gmail.com"
    port = 587
    load_dotenv()

    sender_email=os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = recipient_email

    message_text = MIMEText(html_message, "html")
    message.attach(message_text)

    if attachment_path:
        with open(attachment_path, "rb") as attachment:
            message_text = MIMEBase("application", "octet-stream")
            message_text.set_payload(attachment.read())

        encoders.encode_base64(message_text)
        message_text.add_header(
            "Content-Disposition",
            "attachment", filename=attachment_path
        )

    message.attach(message_text)
    context = ssl.create_default_context()

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient_email, message.as_string())
    except Exception as e:
        print(e)
    finally:
        server.quit()



