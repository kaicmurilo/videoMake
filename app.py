import requests
import os
import json
import time
from dotenv import load_dotenv
import re
from datetime import datetime
from functions.roteiro import gerar_roteiro_e_prompt
from functions.image import gerar_imagem_local
from functions.video import criar_video_json2video, monitorar_video, baixar_video
load_dotenv()


# Execução principal
prompt_ia = """
Crie um roteiro de vídeo motivacional com narrativa nostálgica e reflexiva, com duração mínima de 15 segundos e máxima de 1 minuto.

Retorne a resposta em JSON com os seguintes campos:

{
  "roteiro": "<roteiro textual da narração>",
  "prompt_imagem": "<prompt detalhado para gerar uma imagem que represente o vídeo com máximo de 70 tokens>",
  "prompt_video": "<prompt detalhado para gerar um vídeo que represente o vídeo com máximo de 70 tokens>"
}
"""

resultado = gerar_roteiro_e_prompt(prompt_ia)
narracao = resultado["roteiro"]
prompt_imagem = resultado["prompt_imagem"]
prompt_video = resultado["prompt_video"]

#salvar em um arquivo json com a data e hora da geração
data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
nome_arquivo = f"resultado_{data_hora}.json"
with open(nome_arquivo, "w", encoding="utf-8") as f:
    json.dump(resultado, f, ensure_ascii=False)


print(f"\n📜 Narração:\n{narracao}\n")
print(f"🖼️  Prompt da imagem:\n{prompt_imagem}\n")

folha_imagem = gerar_imagem_local(prompt_imagem)
print(f"🖼️  Imagem gerada: {folha_imagem}\n")

# movie_id = criar_video_json2video(narracao, url_imagem)
# url_final = monitorar_video(movie_id)
# baixar_video(url_final)
