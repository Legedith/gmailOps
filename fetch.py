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

def create_email_database(db_name='email_database.db'):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Create a table to store email data if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                from_address TEXT,
                subject TEXT,
                message TEXT,
                received_datetime TEXT
            )
        ''')

        # Create a table to store labels if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS labels (
            id TEXT PRIMARY KEY NOT NULL
    )
        ''')

        # Create a table to associate emails with labels
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_labels (
                email_id TEXT,
                label_id TEXT,
                FOREIGN KEY (email_id) REFERENCES emails(id),
                FOREIGN KEY (label_id) REFERENCES labels(id),
                PRIMARY KEY (email_id, label_id)
            )
        ''')

        # Commit changes and close the database connection
        conn.commit()
        conn.close()

    except sqlite3.Error as error:
        print(f"Error creating database tables: {error}")

def fetch_emails_with_details(label_ids=['INBOX'], max_results=20):
    try:
        # Authenticate with Gmail API
        creds = authenticate_gmail()

        # Build the Gmail API service
        service = build('gmail', 'v1', credentials=creds)

        # Fetch a list of email messages with specified label_ids and max_results
        results = service.users().messages().list(
            userId='me', labelIds=label_ids, maxResults=max_results).execute()
        messages = results.get('messages', [])

        if not messages:
            print('No emails found with the specified label_ids.')
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
            try:
                payload = payload['parts'][0]
            except:
                pass
            if payload:
                message_body = payload.get('body', {})
                if 'data' in message_body:
                    message_data = message_body['data']
                    # Decode the message data from base64
                    message_text = base64.urlsafe_b64decode(
                        message_data).decode('utf-8')

            email_info = {
                'id': message['id'],
                'from': from_address,
                'subject': subject,
                'message': message_text,
                'received_datetime': received_datetime,
                'label_ids': email_details.get('labelIds', [])
            }
            # print(email_info['label_ids'])
            emails_with_details.append(email_info)

        return emails_with_details
    except HttpError as error:
        print(f'An error occurred while fetching emails: {error}')
        return []

def store_emails_in_database(conn, emails_with_details):
    try:
        cursor = conn.cursor()

        for email_info in emails_with_details:
            # Insert or replace the email in the emails table
            cursor.execute('''
                INSERT OR REPLACE INTO emails (id, from_address, subject, message, received_datetime)
                VALUES (?, ?, ?, ?, ?)
            ''', (email_info['id'], email_info['from'], email_info['subject'], email_info['message'], email_info['received_datetime']))

            # Insert labels into the labels table and associate them with the email
            label_ids = []
            for label_id in email_info.get('label_ids', []):
                label_name = label_id.split('/')[-1]
                cursor.execute('INSERT OR IGNORE INTO labels (id) VALUES (?)', (label_name,))
                label_ids.append(label_name)

            for label_id in label_ids:
                cursor.execute('''
                    INSERT OR IGNORE INTO email_labels (email_id, label_id)
                    VALUES (?, ?)
                ''', (email_info['id'], label_id))

        # Commit changes
        conn.commit()
        print('Emails stored in the database.')

    except sqlite3.Error as error:
        print(f'An error occurred while storing emails in the database: {error}')

def connect_to_database(db_name='email_database.db'):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_name)
        return conn
    except sqlite3.Error as error:
        print(f"Error connecting to the database: {error}")
        return None

import argparse

def main():
    parser = argparse.ArgumentParser(description="Fetch and store emails with details.")
    parser.add_argument("--label_ids", nargs="+", default=['INBOX'], help="Label IDs to filter emails")
    parser.add_argument("--max_results", type=int, default=20, help="Maximum number of emails to fetch")
    parser.add_argument("--db_name", default='email_database.db', help="Database name")

    args = parser.parse_args()

    try:
        # Step 1: Create the email database and tables
        create_email_database(args.db_name)

        # Step 2: Connect to the database
        conn = connect_to_database(args.db_name)
        if conn is not None:
            # Step 3: Fetch email details with provided label_ids and max_results
            emails_with_details = fetch_emails_with_details(args.label_ids, args.max_results)

            # Step 4: Store email details in the database
            if emails_with_details:
                store_emails_in_database(conn, emails_with_details)

            # Close the database connection
            conn.close()
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()



# # to test:
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

# # Connect to the SQLite database
# conn = sqlite3.connect('email_database.db')

# # Create a cursor to execute SQL commands
# cursor = conn.cursor()

# # Print data from the "labels" table
# cursor.execute("SELECT * FROM labels")
# labels = cursor.fetchall()

# print("Labels:")
# for label in labels:
#     print(f"Label ID: {label}")
#     print()

# # Print data from the "email_labels" table
# cursor.execute("SELECT * FROM email_labels")
# email_labels = cursor.fetchall()

# print("Email Labels:")
# for email_label in email_labels:
#     email_id, label_id = email_label
#     print(f"Email ID: {email_id}")
#     print(f"Label ID: {label_id}")
#     print()

# # Close the database connection
# conn.close()
