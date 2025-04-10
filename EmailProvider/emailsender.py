import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

def send_email(sender_email, recipient_name, recipient_email, subject, body):
    # Configure Brevo API key
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = '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'

    # Create an instance of the API client
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    # Build sender and recipient names from emails
    sender_name = get_username_from_email(sender_email)
    recipient_name = recipient_name or get_username_from_email(recipient_email)

    # Define the email payload
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        sender={"name": sender_name, "email": sender_email},
        to=[{"email": recipient_email, "name": recipient_name}],
        subject=subject,
        html_content=generate_email_html(sender_name, sender_email, recipient_name, recipient_email, subject, body)
    )

    try:
        # Send the email
        api_response = api_instance.send_transac_email(send_smtp_email)
        print("✅ Email sent successfully:", api_response)
    except ApiException as e:
        print("❌ Error sending email:", e)


def generate_email_html(sender_name, sender_email, recipient_name, recipient_email, subject, body):
    html_content = f"""{body}"""
    return html_content


def get_username_from_email(email: str) -> str:
    """Extracts and returns the username from an email address."""
    return email.split("@")[0] if "@" in email else email

send_email(
    sender_email="hi@sodeom.com",
    recipient_name="John Doe",
    recipient_email="abdulhadijunaidahmedkhan@gmail.com",
    subject="Test Email via Brevo",
    body="This is a test email sent through Brevo's API."
)
# Uncomment this line to send the email when running the script.