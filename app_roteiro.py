import json
from dotenv import load_dotenv
from datetime import datetime
from functions.roteiro import gerar_roteiro_e_prompt
import os
load_dotenv()

caminho_jsons= 'roteiros'

os.makedirs(caminho_jsons, exist_ok=True)

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
nome_arquivo = f"{caminho_jsons}/resultado_{data_hora}.json"
with open(nome_arquivo, "w", encoding="utf-8") as f:
    json.dump(resultado, f, ensure_ascii=False)

