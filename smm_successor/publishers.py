import logging
import os
import os.path
from typing import Dict, Union

import googleapiclient.discovery
import googleapiclient.errors
import requests
from fastapi import HTTPException
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload

from smm_successor.models.video import VideoInDB, SocialPlatform, VKVideoInfo, YTVideoInfo

logger = logging.getLogger(__name__)


class Publisher:
    def upload(self, video: VideoInDB) -> Union[VKVideoInfo, YTVideoInfo]:
        ...

    def edit_video(self, video: VideoInDB) -> VideoInDB:
        ...

    def delete_video(self, video: VideoInDB) -> Dict:
        ...


class YoutubePublisher(Publisher):
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
              "https://www.googleapis.com/auth/youtube.force-ssl"]

    def __init__(self, client_secrets_file):
        self.client_secrets_file = client_secrets_file

    def get_creds(self):
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
        return youtube

    def upload(self, video: VideoInDB) -> YTVideoInfo:
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        youtube = self.get_creds()
        request = youtube.videos().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": f"{video.info.title}",
                    "description": f"{video.info.description}"
                },
                "status": {
                    "privacyStatus": "private"
                }
            },
            media_body=MediaFileUpload(video.file_path)
        )

        logger.info(f"[YouTube] Start '{video.file_path}' uploading...")

        try:
            response = request.execute()
        except googleapiclient.errors.HttpError:
            raise HTTPException(502, f"Error while uploading video on youtube")

        logger.info(f"[YouTube] '{video.file_path}' uploaded")

        return response

    def edit_video(self, video: VideoInDB):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        youtube = self.get_creds()
        # TODO seems like we need to describe YT VideoInfo model with all attributes
        request = youtube.videos().update(
            part="snippet",
            body={
                "id": video.platform_status[SocialPlatform.youtube]['id'],
                "snippet": {
                    "title": video.info.title,
                    "description": video.info.description,
                    "categoryId": video.platform_status[SocialPlatform.youtube]['snippet']["categoryId"]
                }
            }
        )

        response = request.execute()
        # TODO: solve exception
        if googleapiclient.errors.HttpError:
            raise HTTPException(502, f"Error while updating video: '{response}'")

        return video

    def delete_video(self, video: VideoInDB):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        youtube = self.get_creds()
        request = youtube.videos().delete(
                id=video.platform_status[SocialPlatform.youtube]['id']
            )
        # TODO: understand what returns from request. i can`t..
        response = request.execute()
        print(response.text)
        print(response.json)
        # TODO: solve exception
        # if googleapiclient.errors.HttpError:
        #     raise HTTPException(502, f"Error while deleting video: '{response}'")

        return response


class VKPublisher(Publisher):
    def __init__(self, token):
        self.token = token

    def upload(self, video: VideoInDB) -> VKVideoInfo:
        url = 'https://api.vk.com/method/video.save'
        params = {
            'name': f'{video.info.title}',
            'description': f'{video.info.description}',
            'privacy_view': '3',
            'access_token': f'{self.token}',
            'v': '5.131'
        }

        response = requests.post(url, params=params)
        data = response.json()
        upload_url = data['response']['upload_url']

        files = {'video_file': open(video.file_path, 'rb')}
        logger.info(f"[VK] Start '{video.file_path}' uploading...")
        response = requests.post(upload_url, files=files)

        if not response.ok:
            raise HTTPException(502, f"Error while uploading video: '{response.text}'")

        logger.info(f"[VK] '{video.file_path}' uploaded")


        return response.json()

    def edit_video(self, video: VideoInDB) -> VideoInDB:
        url = 'https://api.vk.com/method/video.edit'
        params = {
            'video_id': f'{video.platform_status[SocialPlatform.vk].video_id}',
            'name': f'{video.info.title}',
            'desc': f'{video.info.description}',
            'access_token': f'{self.token}',
            'v': '5.131'
        }

        response = requests.post(url, params=params)
        if not response.ok:
            raise HTTPException(502, f"Error while updating video: '{response.text}'")

        return video

    def delete_video(self, video: VideoInDB) -> VideoInDB:
        url = 'https://api.vk.com/method/video.delete'
        print(video.platform_status[SocialPlatform.vk].video_id)
        params = {
            'video_id': f'{video.platform_status[SocialPlatform.vk].video_id}',
            'access_token': f'{self.token}',
            'v': '5.131'
        }

        response = requests.post(url, params=params)
        print(response.text)
        # if not response.ok:
        #     raise HTTPException(502, f"Error while deleting video: '{response.text}'")

        return response
