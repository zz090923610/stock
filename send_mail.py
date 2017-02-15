#!/usr/bin/python2
from __future__ import print_function

import argparse
import base64
import os
import pickle
import sys
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httplib2
from apiclient import discovery
from googleapiclient import errors
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://mail.google.com/'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'


# noinspection PyShadowingNames
def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('.')
    credential_dir = os.path.join(home_dir, 'gmail_credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            # noinspection PyUnresolvedReferences
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def create_message(sender, to, subject, message_text):
    """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
    part2 = MIMEText(message_text, 'html')
    message = MIMEMultipart('alternative')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    message.attach(part2)
    return {'raw': base64.urlsafe_b64encode(message.as_string())}


def load_plot_list():
    with open('../stock_data/plots/plot_list.pickle', 'rb') as f:
        return pickle.load(f)


def create_message_with_attachment(
        sender, to, subject, message_text):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msgText = MIMEText(message_text, 'html')
    message.attach(msgText)  # Added, and edited the previous line
    files = load_plot_list()
    print(files)
    for attachment in files:
        print(attachment)
        fp = open('../stock_data/plots/%s' % attachment, 'rb')
        img = MIMEImage(fp.read())
        fp.close()
        img.add_header('Content-ID', '<{}>'.format(attachment))
        message.attach(img)

    return {'raw': base64.urlsafe_b64encode(message.as_string())}


def send_message(gmail_service, user_id, message):
    """Send an email message.

  Args:
    gmail_service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
    try:
        message = (gmail_service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    """Shows basic usage of the Gmail API.

        Creates a Gmail API service object and outputs a list of label names
        of the user's Gmail account.
        """
    try_login = False
    try_send = False
    recipient = ''
    title = ''
    content_file = ''
    data = ''
    without_attachment = False
    for (idx, arg) in enumerate(sys.argv):
        if arg == '-l':
            try_login = True
        elif arg == '-s':
            try_login = True
            try_send = True
            recipient = sys.argv[idx + 1]
            title = sys.argv[idx + 2].decode('utf-8')
            content_file = sys.argv[idx + 3]
            with open(content_file, 'r') as myfile:
                data = myfile.read()
        elif arg == '-n':
            without_attachment = True
    if try_login:
        flags = argparse.Namespace(auth_host_name='localhost', auth_host_port=[8080, 8090], logging_level='ERROR',
                                   noauth_local_webserver=False)
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        service = discovery.build('gmail', 'v1', http=http)

        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
        else:
            print('Labels:')
            for label in labels:
                print(label['name'])
        if try_send:
            if not without_attachment:
                msg = create_message_with_attachment('me', recipient, title, data)
            else:
                msg = create_message('me', recipient, title, data)
            send_message(service, 'me', msg)
