import os
import googleapiclient.discovery
import googleapiclient.errors
import googleapiclient.http
import google_auth_oauthlib.flow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def authenticate_youtube():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    client_secrets_file = "client_secrets.json"

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file,
        SCOPES
    )
    credentials = flow.run_local_server()
    youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)
    return youtube

def upload_video(youtube):
    request_body = {
        "snippet": {
            "categoryId": "22",
            "title": "Quantas Vezes você já se sabotou hoje?",
            "description": "",
            "tags": ["auto"]
        },
        "status": {
            "privacyStatus": "private"
        }
    }

    media_file = googleapiclient.http.MediaFileUpload(
        'video.mp4',
        chunksize=-1,
        resumable=True
    )
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploading: {int(status.progress() * 100)}%")

    print(f'Video ID: {response["id"]}')

if __name__ == "__main__":
    youtube = authenticate_youtube()
    upload_video(youtube)
