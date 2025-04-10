import smtplib
from email.message import EmailMessage

def send_test_email():
    # Create an email message
    msg = EmailMessage()
    msg['Subject'] = 'Test Email from smtplib'
    msg['From'] = 'sender@example.com'
    msg['To'] = 'abdulhadi@sodeom.com'
    msg.set_content('This is a test email body to check SMTP server functionality.')

    try:
        # Connect to the local SMTP server on port 25
        with smtplib.SMTP('localhost', 25) as server:
            server.send_message(msg)
        print("Test email sent successfully.")
    except Exception as e:
        print("Failed to send test email:", e)

if __name__ == "__main__":
    send_test_email()