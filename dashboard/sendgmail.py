# Import Packages For Email
from email.message import EmailMessage
import ssl
import smtplib

def sendingMail(email_receiver, subject, body):
    email_sender = "officialbotproffesor@gmail.com"
    email_password = "qijo qlev rczo yhah"
    emailMessage = EmailMessage()
    emailMessage['From'] = email_sender
    emailMessage['To'] = email_receiver
    emailMessage['Subject'] = subject
    emailMessage.set_content(body)

    # Define Smtp connection
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465 , context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, emailMessage.as_string())
        print("Message Sent Successfully!")