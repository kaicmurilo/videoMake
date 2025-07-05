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
    download_dir = Path.home() / "Downloads"
    video_path = download_dir / f"{title}.mp4"
    thumb_path = download_dir / f"{title}.jpg"

    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=Path(USER_DATA_DIR).expanduser(),
            headless=False,
            ignore_default_args=["--enable-automation"],
            args=["--disable-blink-features=AutomationControlled"],
            viewport={"width": 1280, "height": 800},
        )
        page = ctx.new_page()
        page.goto("https://tubefy.io/login")
        if "login" in page.url:
            print("➡️ Faça login com Google...")
            page.wait_for_url("https://tubefy.io/", timeout=0)

        page.goto("https://tubefy.io/p_shorts")
        page.click('button:has-text("Novo Projeto")')
        page.fill('div:has-text("Título") input', title)
        page.select_option('select.bubble-element.Dropdown', label="Estoicismo")
        page.fill('div:has-text("Prompt para ideia do vídeo") textarea', assunto)

        # Avançar duas vezes
        avancar_btn = page.locator('button:has-text("Avançar")')
        avancar_btn.wait_for(state='visible', timeout=600000)
        avancar_btn.click()
        
        gerar_btn = page.locator('button:has-text("Gerar")')
        gerar_btn.wait_for(state='visible', timeout=600000)
        
        avancar_btn_historia = page.locator('button:has-text("Avançar")')
        avancar_btn_historia.wait_for(state='visible', timeout=600000)
        avancar_btn_historia.click()

        # antes de gerar, clicar na div que contém "Center"
        center_div = page.locator('div:has-text("Center")')
        center_div.wait_for(state='visible', timeout=600000)
        center_div.click()
        
        # Gerar Vídeo
        gerar_video_btn = page.locator('button:has-text("Gerar")')
        gerar_video_btn.wait_for(state='visible', timeout=600000)
        gerar_video_btn.click()
        
        
        

        # Baixar vídeo
        page.wait_for_selector('button:has-text("Baixar Vídeo")', timeout=600000)
        page.click('button:has-text("Baixar Vídeo")')
        page.wait_for_selector('.short-download-link a', timeout=600000)
        video_url = page.get_attribute('.short-download-link a', 'href')
        download_file(video_url, video_path)

        # Baixar thumbnail
        page.click('button:has-text("Baixar Thumbnail")')
        page.wait_for_selector('.short-download-link a', timeout=600000)
        thumb_url = page.get_attribute('.short-download-link a', 'href')
        download_file(thumb_url, thumb_path)

        ctx.close()

    return video_path, thumb_path

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
    title = data["title"]
    assunto = data["assunto"]
    assunto = TUBFY_PROMPT.replace("[ASSUNTO]", assunto)
    video_file, thumbnail_file = generate_short(title, assunto)
    print(f"✅ Vídeo salvo em: {video_file}")
    print(f"✅ Thumbnail salva em: {thumbnail_file}")
