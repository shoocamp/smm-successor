import logging
import os
import os.path

import googleapiclient.discovery
import googleapiclient.errors
import requests
from fastapi import HTTPException
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload

logger = logging.getLogger(__name__)


class Publisher:
    def upload(self, file_path, title, description):
        ...


class YoutubePublisher(Publisher):
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

    def __init__(self, client_secrets_file):
        self.client_secrets_file = client_secrets_file

    def upload(self, file_path, title, description):
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"

        # Get credentials and create an API client
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
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
            media_body=MediaFileUpload(file_path)
        )

        logger.info(f"[YouTube] Start '{file_path}' uploading...")

        try:
            response = request.execute()
        except googleapiclient.errors.HttpError:
            raise HTTPException(502, f"Error while uploading video: '{response.text}'")

        logger.info(f"[YouTube] '{file_path}' uploaded")

        return response


class VKPublisher(Publisher):
    def __init__(self, token):
        self.token = token

    def upload(self, file_path, title, description):
        url = 'https://api.vk.com/method/video.save'
        params = {
            'name': f'{title}',
            'description': f'{description}',
            'privacy_view': '3',
            'access_token': f'{self.token}',
            'v': '5.131'
        }

        response = requests.post(url, params=params)
        data = response.json()
        upload_url = data['response']['upload_url']

        files = {'video_file': open(file_path, 'rb')}
        logger.info(f"[VK] Start '{file_path}' uploading...")
        response = requests.post(upload_url, files=files)

        if not response.ok:
            raise HTTPException(502, f"Error while uploading video: '{response.text}'")

        logger.info(f"[VK] '{file_path}' uploaded")

        return response.json()

    # TODO: add logic for different quantity of parameters changing
    def edit_data(self, video_id, new_title, new_description):
        url = 'https://api.vk.com/method/video.edit'
        params = {
            'video_id': f'{video_id}',
            'name': f'{new_title}',
            'desc': f'{new_description}',
            'access_token': f'{self.token}',
            'v': '5.131'
        }

        response = requests.post(url, params=params)
        print(response.content)
        return response.text


