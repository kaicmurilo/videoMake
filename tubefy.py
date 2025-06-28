import os
import sys
import requests
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()
USER_DATA_DIR = os.getenv("CHROME_USER_DATA_DIR")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/v1/completions")
TAGS_TK = os.getenv("TAGS_TK")
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

def generate_short(title: str, script: str) -> tuple[Path, Path]:
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
        page.select_option('select.bubble-element.Dropdown', label="Motivacional")
        page.fill('div:has-text("Prompt para ideia do vídeo") textarea', script)

        # Avançar duas vezes
        page.click('button:has-text("Avançar")')
        page.wait_for_selector('button:has-text("Avançar")', timeout=600000)
        page.click('button:has-text("Avançar")')

        # Gerar
        page.wait_for_selector('button:has-text("Gerar")', timeout=600000)
        page.click('button:has-text("Gerar")')

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

if __name__ == "__main__":
    title = "Vídeo Motivacional"
    prompt = "Crie um roteiro motivacional curto para vídeo de até 30 segundos."
    script = call_ollama("llama3", prompt)
    video_file, thumbnail_file = generate_short(title, script)
    print(f"✅ Vídeo salvo em: {video_file}")
    print(f"✅ Thumbnail salva em: {thumbnail_file}")
