
import os
import sys
import json
import argparse
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


class YT:
    def __init__(self, youtube):
        self.youtube = youtube

    def get_service(self):
        flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, SCOPES)
        creds = flow.run_console()
        return build("youtube", "v3", credentials=creds)

    def upload_video(self, file_path, title, description, tags, category_id, privacy):
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category_id
            },
            "status": {
                "privacyStatus": privacy
            }
        }
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
        request = self.youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        response = None
        while response is None:
            status, response = request.next_chunk()
        return response


    def list_video_categories(self, region_code='BR'):
        request = self.youtube.videoCategories().list(
            part='snippet',
            regionCode=region_code
        )
        response = request.execute()
        return {item['snippet']['title']: item['id'] for item in response.get('items', [])}
    
    
    # resp = upload_video(
    #     youtube,
    #     args.file,
    #     args.title,
    #     args.description,
    #     args.tags,
    #     args.category,
    #     args.privacy
    # )
    # print(json.dumps(resp, indent=2))