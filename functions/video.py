import os
import requests
import json
import time

def criar_video_json2video(narracao, url_imagem):
    payload = {
        "scenes": [
            {
                "elements": [
                    {
                        "type": "voice",
                        "text": narracao,
                        "voice": "azure",
                        "language": "pt-BR"
                    },
                    {
                        "type": "text",
                        "text": "Motivação e reflexão",
                        "x": "center",
                        "y": "top",
                        "font": "Arial",
                        "size": 48,
                        "color": "#FFFFFF"
                    },
                    {
                        "type": "image",
                        "source": url_imagem,
                        "fit": "cover",
                        "duration": "media"
                    }
                ]
            }
        ],
        "width": 1080,
        "height": 1920,
        "fps": 30
    }

    response = requests.post(
        url="https://api.json2video.com/v1/movies",
        headers={
            "Authorization": f"Bearer {os.getenv('JSON2VIDEO_API_KEY')}",
            "Content-Type": "application/json"
        },
        data=json.dumps(payload)
    )

    return response.json()["movieId"]


def monitorar_video(movie_id):
    print(f"⏳ Monitorando vídeo ID {movie_id}...")
    status = None
    while status != "finished":
        time.sleep(5)
        response = requests.get(
            f"https://api.json2video.com/v1/movies/{movie_id}",
            headers={"Authorization": f"Bearer {os.getenv('JSON2VIDEO_API_KEY')}"}
        )
        data = response.json()
        status = data.get("status")
        print(f"Status atual: {status}")
    return data.get("outputUrl")


def baixar_video(url, nome_arquivo="video_final.mp4"):
    print(f"⬇️  Baixando vídeo de: {url}")
    response = requests.get(url)
    with open(nome_arquivo, 'wb') as f:
        f.write(response.content)
    print(f"✅ Vídeo salvo como: {nome_arquivo}")

