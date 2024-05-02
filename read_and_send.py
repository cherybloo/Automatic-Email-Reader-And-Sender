import os.path
import base64
import email
import re
import sys

import mimetypes
from email.message import EmailMessage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
# Default SCOPES (Readonly)
#SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Full access to the account's mailboxes
SCOPES = ["https://mail.google.com/"]

def main():
	user_email = input("Enter your email address: ")
	maxNumbers = input("Enter the maximum numbers: ")
	query = input("Query: ")

	service = gmail_authentication()
	get_messages_id(service,query,maxNumbers, user_email) 
	# service -> what kind of service do you want to retrieve
	# query -> (string) that you want to search from the mailboxes
	# maxNumbers -> (integer) maximal number of messages that you want to retrieve from your mailboxes

# get id -> get message -> get recipients -> send the email text

# Handle the GMAIL authentication
def gmail_authentication():
	creds = None

	if os.path.exists("token.json"):
		creds = Credentials.from_authorized_user_file("token.json", SCOPES)
	# If none's found, let the user log in
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(
				"credentials.json", SCOPES
			)
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open("token.json", "w") as token:
			token.write(creds.to_json())
	# Return service
	return build("gmail", "v1", credentials=creds)

def send_message(service, recipients, user_email):
    for target_email in recipients:
        try:
            message = MIMEMultipart()
            message['To'] = target_email
            message['From'] = user_email
            message['Subject'] = 'Bruh'
            html_content = "<div dir=\"ltr\"><img src=\"https://media1.tenor.com/m/_TemusfqiUMAAAAC/unbelievable-the-office.gif\" width=\"452\" height=\"252\"><br></div>"
            html_part = MIMEText(html_content, 'html')
            message.attach(html_part)

            # encoded message
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            create_message = {"raw": encoded_message}
            send_message = (
                service.users()
                .messages()
                .send(userId="me", body=create_message)
                .execute()
            )
            print(f'Message Id: {send_message["id"]}')
        except HttpError as error:
            print(f"An error occurred: {error}")
            send_message = None

def get_messages_body(service, message_id, user_email):
	recipients = []
	try:
		for messageId in message_id: # Iterate through the message Id
			message = service.users().messages().get(
				userId = "me",
				id = messageId,
				format = "raw"
			).execute()
			mime_msg = email.message_from_bytes(base64.urlsafe_b64decode(message["raw"]))

			msg_from = mime_msg['from']
			msg_to = mime_msg['to']
			msg_subject = mime_msg['subject']
			pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
			recipient = re.findall(pattern,msg_from)[0]
			if recipient not in recipients and recipient != user_email:
				recipients.append(recipient)
		send_message(service, recipients, user_email)
	except HttpError as error:
		print(f"An error occurred: {error}")

def get_messages_id(service, query, maxNumbers, user_email):
	# Call the API
	try:
		messages = service.users().messages().list(
			userId = "me",
			maxResults = maxNumbers,
			q = query,
		).execute()
		messages_response = messages.get("messages", [])
		if not messages_response:
			print("The query doesn't match any messages")
			return
		# print(messages_response)
		message_id = []
		for id in messages_response:
			message_id.append(id['id'])
		print(message_id)
		get_messages_body(service, message_id, user_email)
	except HttpError as error:
		print(f"An error occurred: {error}")

if __name__ == "__main__":
	main()