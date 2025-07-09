import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import json
import re
import ast
import time

load_dotenv()
USER_DATA_DIR = os.getenv("CHROME_USER_DATA_DIR")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/v1/completions")
TAGS_TK = os.getenv("TAGS_TK")
PROMPT_OLLAMA = os.getenv("PROMPT_OLLAMA")
TUBFY_PROMPT = os.getenv("TUBFY_PROMPT")
CLIENT_SECRETS_FILE = "client_secrets.json"

if not USER_DATA_DIR:
    print("⚠️ Defina CHROME_USER_DATA_DIR no .env")
    sys.exit(1)

def call_ollama(model: str, prompt: str) -> str:
    resp = requests.post(
        OLLAMA_URL,
        json={"model": model, "prompt": prompt}
    )
    resp.raise_for_status()
    data = resp.json()
    if "choices" in data:
        choice = data["choices"][0]
        if "text" in choice:
            return choice["text"].strip()
        if "message" in choice and "content" in choice["message"]:
            return choice["message"]["content"].strip()
    return data.get("completion", "").strip()

def download_file(url: str, path: Path):
    resp = requests.get(url)
    resp.raise_for_status()
    path.write_bytes(resp.content)

def generate_short(title: str, assunto: str) -> tuple[Path, Path]:
    base_dir = Path("videos") / title
    base_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=Path(USER_DATA_DIR).expanduser(),
            headless=False,
            ignore_default_args=["--enable-automation"],
            args=["--disable-blink-features=AutomationControlled"],
            viewport={"width": 1280, "height": 800},
            downloads_path=base_dir,
            accept_downloads=True
        )
        page = ctx.new_page()
        page.goto("https://tubefy.io/login")
        if "login" in page.url:
            print("➡️ Faça login com Google...")
            page.wait_for_url("https://tubefy.io/", timeout=0)

        page.goto("https://tubefy.io/p_shorts")
        print("➡️ Criando novo projeto...")
        page.click('button:has-text("Novo Projeto")')
        page.fill('div:has-text("Título") input', title)
        print("➡️ Selecionando assunto...")
        page.select_option('select.bubble-element.Dropdown', label="Estoicismo")
        print("➡️ Digitando prompt...")
        page.fill('div:has-text("Prompt para ideia do vídeo") textarea', assunto)
        print("➡️ Avançando...")
        # Avançar duas vezes
        avancar_btn = page.locator('button:has-text("Avançar")')
        avancar_btn.wait_for(state='visible', timeout=600000)
        avancar_btn.click()
        
        # print("➡️ Gerando história...")
        # gerar_btn = page.locator('button:has-text("Gerar")')
        # gerar_btn.wait_for(state='visible', timeout=600000)
        
        try:
            page.wait_for_selector("text=Criando sua história...", state="visible", timeout=60000)
            print("➡️ Aguardando História...")
            page.wait_for_selector("text=Criando sua história...", state="hidden", timeout=120000)
            print("➡️ História gerada com sucesso!")
        except PlaywrightTimeoutError:
            time.sleep(150)
            pass
        
        
        
        
        avancar_btn_historia = page.locator('button.baUaBaLg:has-text("Avançar")')
        for attempt in range(3):
            try:
                print(f"➡️ Tentativa {attempt+1} de clicar Avançar...")
                avancar_btn_historia.wait_for(state='visible', timeout=60000)
                avancar_btn_historia.click()
                break
            except PlaywrightTimeoutError:
                if attempt == 2:
                    raise
                time.sleep(5)

        print("➡️ Aguardando Div Center...")
        # antes de gerar, clicar na div que contém "Center"
        page.locator('div.clickable-element:has-text("Center")').click()
        print("➡️ Aguardando Div Center...")
        
        # Gerar Vídeo
        print("➡️ Clicando no Botão de Gerar...")
        page.get_by_role("button", name="Gerar").click()
        
        
        try:
            page.wait_for_selector("text=Criando seu vídeo....", state="visible", timeout=60000)
            print("➡️ Aguardando Vídeo...")
            page.wait_for_selector("text=Criando seu vídeo....", state="hidden", timeout=120000)
            print("➡️ Vídeo gerado com sucesso!")
        except PlaywrightTimeoutError:
            time.sleep(150)
            pass
        
        
        # aguardar preview e baixar vídeo
        print("➡️ Aguardando Preview...")
        page.locator('button:has-text("Baixar Vídeo")').click()
        page.locator('video#preview').wait_for(state='attached', timeout=600000)
        print("➡️ Baixando Vídeo...")
        #entra na pasta e renomeia o arquivo baixado para f"{title}.mp4" base_dir
        time.sleep(10)
        files = list(base_dir.iterdir())
        file_no_ext = next((f for f in files if f.is_file() and f.suffix == ""), None)
        if file_no_ext:
            destino = base_dir / f"{title}.mp4"
            file_no_ext.rename(destino)
            print(f"✅ Vídeo renomeado para: {destino.name}")
        else:
            print("⚠️ Arquivo de vídeo não encontrado para renomear.")
        


        # baixar thumbnail
        print("➡️ Aguardando Thumbnail...")
        page.locator('button:has-text("Baixar Thumbnail")').click()
        #entra na pasta e renomeia o arquivo baixado para f"{title}.png"
        time.sleep(10)
        files = list(base_dir.iterdir())
        file_no_ext = next((f for f in files if f.is_file() and f.suffix == ""), None)
        if file_no_ext:
            destino = base_dir / f"{title}.png"
            file_no_ext.rename(destino)
            print(f"✅ Thumbnail renomeado para: {destino.name}")
        else:
            print("⚠️ Arquivo de thumbnail não encontrado para renomear.")

        print("➡️ Fechando Browser...")
        ctx.close()

def get_json_response(script: str) -> dict:
    script = script.strip().lstrip("'\"").rstrip("'\"")
    m = re.search(r'(\{.*\})', script, re.DOTALL)
    if not m:
        pattern = re.compile(
            r'"title"\s*:\s*"(?P<title>[^"]+)"|'      
            r'"assunto"\s*:\s*"(?P<assunto>[^"]+)',   
            re.DOTALL
        )
        matches = pattern.finditer(script)
        data = {}
        for match in matches:
            if match.group('title'):
                data['title'] = match.group('title')
            if match.group('assunto'):
                data['assunto'] = match.group('assunto')
        return data
    block = m.group(1)
    try:
        return json.loads(block)
    except json.JSONDecodeError:
        try:
            return ast.literal_eval(block)
        except Exception:
            return {}
    
if __name__ == "__main__":
    script = call_ollama("llama3", PROMPT_OLLAMA)
    data = get_json_response(script)
    title = data["title"] or data["titulo"]
    assunto = data["assunto"]
    assunto = TUBFY_PROMPT.replace("[ASSUNTO]", assunto)
    generate_short(title, assunto)
