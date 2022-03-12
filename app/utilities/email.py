import os, smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_mail(subject, html_message, recipient_email, attachment=None):
    smtp_server = "smtp.gmail.com"
    port = 587
    sender_email="boorsokkaimak@gmail.com"
    password = "Sulochana2493!"

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = recipient_email

    message_text = MIMEText(html_message, "html")
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



