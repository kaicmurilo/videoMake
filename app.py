import requests
import os
import json
import time
from dotenv import load_dotenv
import re
from functions.roteiro import gerar_roteiro_e_prompt
from functions.image import gerar_imagem_huggingface
from functions.video import criar_video_json2video, monitorar_video, baixar_video
load_dotenv()


# Execução principal
prompt_ia = """
Crie um roteiro de vídeo motivacional com narrativa nostálgica e reflexiva, com duração mínima de 15 segundos e máxima de 1 minuto.

Retorne a resposta em JSON com os seguintes campos:

{
  "roteiro": "<roteiro textual da narração>",
  "prompt_imagem": "<prompt detalhado para gerar uma imagem que represente o vídeo>"
}
"""

resultado = gerar_roteiro_e_prompt(prompt_ia)
narracao = resultado["roteiro"]
prompt_imagem = resultado["prompt_imagem"]

print(f"\n📜 Narração:\n{narracao}\n")
print(f"🖼️  Prompt da imagem:\n{prompt_imagem}\n")

url_imagem = gerar_imagem_huggingface(prompt_imagem)
print(f"🖼️  Imagem gerada: {url_imagem}\n")

movie_id = criar_video_json2video(narracao, url_imagem)
url_final = monitorar_video(movie_id)
baixar_video(url_final)
