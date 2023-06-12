import os

import googleapiclient.discovery
import googleapiclient.errors

from googleapiclient.http import MediaFileUpload

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def upload(file, title, description):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "/Users/sergeyzaitsev/PycharmProjects/smm-successor/youtube_auth/client_secret_2.json"

    # Get credentials and create an API client
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        print("1exist?", creds, "valid?", creds.valid)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        print("2exist?", creds, "valid?", creds.valid)
        if creds and creds.expired and creds.refresh_token:  # можно попробовать добить not к creds.expired оригинальному коду
            print("3exist?", creds, "valid?", creds.valid)
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)
            print("4exist?", creds, "valid?", creds.valid)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=creds)

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": f"{title}",
                "description": f"{description}"
            },
            "status": {
                "privacyStatus": "private"
            }
        },
        media_body=MediaFileUpload(file)
    )
    response = request.execute()

    return response
