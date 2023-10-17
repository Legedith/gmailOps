import base64
import mimetypes
import os
from email.message import EmailMessage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fetch import authenticate_gmail
from googleapiclient.discovery import build
# Use the Gmail API to mark the email
creds = authenticate_gmail()
service = build('gmail', 'v1', credentials=creds)

def create_email_message(to, sender, subject, message, attachment_path=None):
    """Create an email message with optional attachment.
    Args:
        to: The recipient's email address.
        sender: The sender's email address.
        subject: The email subject.
        message: The email message content.
        attachment_path: The file path to an optional attachment.
    Returns:
        An email message object.
    """
    mime_message = EmailMessage()
    mime_message['To'] = to
    mime_message['From'] = sender
    mime_message['Subject'] = subject
    mime_message.set_content(message)
    mime_message.add_alternative(message, subtype='html')

    if attachment_path:
        attach_file(mime_message, attachment_path)

    return mime_message

def attach_file(mime_message, attachment_filename):
    """Attach a file to an email message.
    Args:
        message: The email message to attach the file to.
        file_path: The path to the file to be attached.
    """
    type_subtype, _ = mimetypes.guess_type(attachment_filename)
    maintype, subtype = type_subtype.split('/')

    with open(attachment_filename, 'rb') as fp:
        attachment_data = fp.read()
    # give the attachement a name
    # retreive the name form the path
    filename = os.path.basename(attachment_filename) 
    mime_message.add_attachment(attachment_data, maintype, subtype, filename=filename)
    # mime_message.add_attachment(attachment_data, maintype, subtype)


def send_email_with_attachment(to, sender, subject, message, attachment_path=None):
    """Send an email with an optional attachment.
    Args:
        to: The recipient's email address.
        sender: The sender's email address.
        subject: The email subject.
        message: The email message content.
        attachment_path: The file path to an optional attachment.
    Returns:
        The message ID of the sent email.
    """
    try:
        email_message = create_email_message(to, sender, subject, message, attachment_path)
        encoded_message = base64.urlsafe_b64encode(email_message.as_bytes()).decode()
        create_message = {
            'raw': encoded_message
        }
        send_message = service.users().messages().send(userId="me", body=create_message).execute()
        return send_message['id']
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None


