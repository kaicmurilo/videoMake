from huggingface_hub import InferenceClient
from diffusers import StableDiffusionPipeline
from PIL import Image
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel, ImageGenerationResponse
import torch
import os

MODELOS = [
    "runwayml/stable-diffusion-v1-5",
    "stabilityai/stable-diffusion-2",
    "dreamlike-art/dreamlike-photoreal-2.0",
    "nitrosocke/redshift-diffusion",
    "prompthero/openjourney"
]

PROJECT_ID = os.getenv("GOOGLEPROJECT") 
LOCATION = "us-central1"
OUTPUT_FILE = "imagem_gerada_google.png"

CAMINHO_IMAGEM = "saida.png"


def gerar_imagem_local(prompt: str) -> str:
    print("⚙️ Gerando imagem localmente com diffusers...")

    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16,
        use_auth_token=True  # requer login via huggingface-cli login
    ).to("cuda")

    pipe.enable_attention_slicing()
    pipe.enable_model_cpu_offload()  # otimiza uso em placas com baixa VRAM

    imagem = pipe(prompt, num_inference_steps=20).images[0]
    imagem.save(CAMINHO_IMAGEM)
    print("✅ Imagem gerada localmente.")
    return CAMINHO_IMAGEM

# --- BLOCO DE EXECUÇÃO ---
if __name__ == "__main__":
    meu_prompt = "Um astronauta surfando em uma onda cósmica de nebulosas, ultra realista, arte digital"
    gerar_imagem_local(meu_prompt)