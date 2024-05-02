import os.path
import json
import base64

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
	
	# Return all the services
	return build("gmail", "v1", credentials=creds)

service = gmail_authentication()

# service -> what kind of service do you want to retrieve
# query -> (string) that you want to search from the mailboxes
# maxNumbers -> (integer) maximal number of messages that you want to retrieve from your mailboxes
def get_messages_body(service, message_id):
	messages = []
	for messageId in message_id: # Iterate through the message Id
		message = service.users().messages().get(
			userId = "me",
			id = messageId,
			format = "raw"
		).execute()
		print(message["snippet"],end="\n\n")

def get_messages_id(service, query, maxNumbers):
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
		#print(message_id)
		get_messages_body(service, message_id)
		#return message_id

	except HttpError as error:
		# TODO(developer) - Handle errors from gmail API.
		print(f"An error occurred: {error}")


get_messages_id(service,"leider",2)