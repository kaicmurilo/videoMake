import os
import requests
import json
import re


def gerar_roteiro_e_prompt(prompt):
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.getenv('OPEN_ROUTER_KEY')}",
            "Content-Type": "application/json"
        },
        data=json.dumps({
            "model": os.getenv("OPEN_ROUTER_MODEL"),
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
    )

    content = response.json()['choices'][0]['message']['content']

    # Tentar extrair bloco JSON com regex
    match = re.search(r'{.*}', content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as e:
            print("❌ JSON inválido extraído:")
            print(match.group(0))
            raise e
    else:
        print("❌ Nenhum JSON encontrado no conteúdo da IA:")
        print(content)
        raise ValueError("JSON não encontrado")
