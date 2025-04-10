import asyncio
import requests
from email import message_from_bytes
from aiosmtpd.controller import Controller

class MyHandler:
    async def handle_DATA(self, server, session, envelope):
        # Parse the raw email content
        msg = message_from_bytes(envelope.content)
        subject = msg.get('Subject', '(No Subject)')
        # Handle multipart messages or plain text:
        if msg.is_multipart():
            # Join parts if needed, here we just take the first part for simplicity
            body = ""
            for part in msg.walk():
                # Ignore attachments and only get text parts
                if part.get_content_type() == "text/plain":
                    body += part.get_payload(decode=True).decode(part.get_content_charset('utf-8'), errors='replace')
        else:
            body = msg.get_payload(decode=True).decode(msg.get_content_charset('utf-8'), errors='replace')

        print(f"Received email from {envelope.mail_from}")
        print("To:", ', '.join(envelope.rcpt_tos))
        print("Subject:", subject)
        print("Body:", body)

        # Prepare the data for the API request
        data = {
            "sender": envelope.mail_from,
            "recipient": ', '.join(envelope.rcpt_tos),
            "subject": subject,
            "body": body
        }

        # Define the API request details
        url = 'https://sodi.pythonanywhere.com/api/send'
        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': 'supersecretapikey123'
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()  # Raise an error for bad responses
            print("API Response:", response.json())
        except requests.exceptions.RequestException as e:
            print("Error sending request to API:", e)
        
        return '250 OK'

async def main():
    handler = MyHandler()
    # Ensure port 25 is free (or change to a different port if running with privileges issues)
    controller = Controller(handler, port=25)
    controller.start()

    print("Server is running on port 25...")
    await asyncio.Event().wait()  # Keep the server running

if __name__ == "__main__":
    asyncio.run(main())