from __future__ import print_function
import sqlite3
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
# Define the Gmail API scope so we can read emails, move emails, add or remove labels, and mark as read, unread
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


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


def fetch_emails_with_details():
    try:
        # Authenticate with Gmail API
        creds = authenticate_gmail()

        # Build the Gmail API service
        service = build('gmail', 'v1', credentials=creds)

        # Fetch a list of email messages from the inbox
        results = service.users().messages().list(
            userId='me', labelIds=['INBOX'], maxResults=20).execute()
        messages = results.get('messages', [])

        if not messages:
            print('No emails found in the inbox.')
            return []

        emails_with_details = []

        for message in messages:
            # Get the full email message details
            email_details = service.users().messages().get(
                userId='me', id=message['id']).execute()

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
            # print(payload.keys())
            try:
                payload = payload['parts'][0]
            except:
                pass
            # print('------------------------------------------------------------------')
            if payload:
                message_body = payload.get('body', {})
                # print(message_body)
                if 'data' in message_body:
                    message_data = message_body['data']
                    # You may need to decode the message data from base64
                    message_text = base64.urlsafe_b64decode(
                        message_data).decode('utf-8')

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


def store_emails_in_database(emails_with_details):
    try:
        conn = sqlite3.connect('email_database.db')
        cursor = conn.cursor()

        for email_info in emails_with_details:
            # some emails might already be there, we will just modify them
            cursor.execute('''
                INSERT OR REPLACE INTO emails (id, from_address, subject, message, received_datetime)
                VALUES (?, ?, ?, ?, ?)
            ''', (email_info['id'], email_info['from'], email_info['subject'], email_info['message'], email_info['received_datetime']))
            # cursor.execute('''
            #     INSERT INTO emails (id, from_address, subject, message, received_datetime)
            #     VALUES (?, ?, ?, ?, ?)
            # ''', (email_info['id'], email_info['from'], email_info['subject'], email_info['message'], email_info['received_datetime']))

        conn.commit()
        conn.close()
        print('Emails stored in the database.')

    except sqlite3.Error as error:
        print(
            f'An error occurred while storing emails in the database: {error}')


if __name__ == '__main__':

    # Connect to the SQLite database (create a new one if it doesn't exist)
    conn = sqlite3.connect('email_database.db')

    # Create a cursor to execute SQL commands
    cursor = conn.cursor()

    # Create a table to store email data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY,
            from_address TEXT,
            subject TEXT,
            message TEXT,
            received_datetime TEXT
        )
    ''')

    # Fetch emails with additional details
    emails_with_details = fetch_emails_with_details()

    if emails_with_details:
        store_emails_in_database(emails_with_details)

    # Close the database connection
    conn.close()


# to test:
# import sqlite3

# # Connect to the SQLite database
# conn = sqlite3.connect('email_database.db')

# # Create a cursor to execute SQL commands
# cursor = conn.cursor()

# # Execute an SQL query to retrieve data from the "emails" table
# cursor.execute("SELECT * FROM emails")

# # Fetch all the rows
# rows = cursor.fetchall()

# # Loop through the rows and print the data
# for row in rows:
#     id, from_address, subject, message, received_datetime = row
#     print(f"ID: {id}")
#     print(f"From: {from_address}")
#     print(f"Subject: {subject}")
#     # print(f"Message: {message}")
#     print(f"Received Date/Time: {received_datetime}")
#     print()

# # Close the database connection
# conn.close()