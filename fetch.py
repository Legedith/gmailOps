from __future__ import print_function
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
# Define the Gmail API scope for read-only access
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None

    # The file token.json stores the user's access and refresh tokens and is created
    # automatically during the initial authorization.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def fetch_emails():
    try:
        # Authenticate with Gmail API
        creds = authenticate_gmail()

        # Build the Gmail API service
        service = build('gmail', 'v1', credentials=creds)

        # Fetch a list of email messages from the inbox
        # results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
        results = service.users().messages().list(userId='me', labelIds=['happyfox'], maxResults=10).execute()
        messages = results.get('messages', [])

        if not messages:
            print('No emails found in the inbox.')
            return []

        return messages
    except HttpError as error:
        print(f'An error occurred while fetching emails: {error}')
        return []

# if __name__ == '__main__':
#     # Fetch emails and store them in the "messages" list
#     messages = fetch_emails()

#     if messages:
#         print(f'Number of emails in the inbox: {len(messages)}')
#         print('Message IDs:')
#         for message in messages:
#             print(message['id'])
    

def fetch_emails_with_details():
    try:
        # Authenticate with Gmail API
        creds = authenticate_gmail()

        # Build the Gmail API service
        service = build('gmail', 'v1', credentials=creds)

        # Fetch a list of email messages from the inbox
        results = service.users().messages().list(userId='me', labelIds=['Label_8803298595243364442'], maxResults=10).execute()
        messages = results.get('messages', [])

        if not messages:
            print('No emails found in the inbox.')
            return []

        emails_with_details = []

        for message in messages:
            # Get the full email message details
            email_details = service.users().messages().get(userId='me', id=message['id']).execute()

            # Extract desired fields
            from_address = None
            subject = None
            message_text = None
            received_datetime = None

            headers = email_details.get('payload', {}).get('headers', [])
            for header in headers:
                if header['name'] == 'From':
                    from_address = header['value']
                elif header['name'] == 'Subject':
                    subject = header['value']
                elif header['name'] == 'Date':
                    received_datetime = header['value']

            payload = email_details.get('payload')
            payload = payload['parts'][0]
            # print('------------------------------------------------------------------')
            if payload:
                message_body = payload.get('body', {})
                # print(message_body)
                if 'data' in message_body:
                    message_data = message_body['data']
                    # You may need to decode the message data from base64
                    message_text = base64.urlsafe_b64decode(message_data).decode('utf-8')

            email_info = {
                'id': message['id'],
                'from': from_address,
                'subject': subject,
                'message': message_text,
                'received_datetime': received_datetime
            }

            emails_with_details.append(email_info)

        return emails_with_details
    except HttpError as error:
        print(f'An error occurred while fetching emails: {error}')
        return []

if __name__ == '__main__':
    # Fetch emails with additional details
    emails_with_details = fetch_emails_with_details()

    if emails_with_details:
        print(f'Number of emails in the inbox: {len(emails_with_details)}')
        print('Email Details:')
        for email_info in emails_with_details:
            print(f'ID: {email_info["id"]}')
            print(f'From: {email_info["from"]}')
            print(f'Subject: {email_info["subject"]}')
            print(f'Message: {email_info["message"]}')
            print(f'Received Date/Time: {email_info["received_datetime"]}')
            print()
