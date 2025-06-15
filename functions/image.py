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


def gerar_imagem_huggingface(prompt: str) -> str:
    for nome_modelo in MODELOS:
        print(f"🎨 Tentando gerar imagem com: {nome_modelo}")
        try:
            client = InferenceClient(model=nome_modelo, token=os.getenv("HUGGING_FACE_KEY"))
            response = client.text_to_image(prompt)

            if response:
                response.save(CAMINHO_IMAGEM)
                print(f"✅ Imagem gerada com sucesso com {nome_modelo}")
                return CAMINHO_IMAGEM

        except Exception as e:
            print(f"⚠️ Falha com {nome_modelo}: {e}")

    print("❌ Todos os modelos da API falharam. Tentando localmente...")
    return gerar_imagem_local(prompt)


def gerar_imagem_google(prompt: str):
    """
    Gera uma imagem usando o modelo Imagen 2 na plataforma Google Vertex AI (método atualizado).
    """
    print(f"⚙️ Iniciando a geração de imagem no Google Vertex AI com o prompt: '{prompt}'")
    
    # Inicializa o SDK do Vertex AI (nova forma)
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    
    # Carrega o modelo de geração de imagem (nova forma)
    # A classe agora é importada diretamente
    model = ImageGenerationModel.from_pretrained("imagegeneration@006")
    
    try:
        # Gera a imagem (a chamada continua a mesma)
        response = model.generate_images(
            prompt=prompt,
            number_of_images=1,
        )
        
        # Salva a imagem gerada em um arquivo
        response.images[0].save(location=OUTPUT_FILE, include_generation_parameters=True)
        
        print(f"✅ Imagem gerada com sucesso e salva como '{OUTPUT_FILE}'")
        return OUTPUT_FILE

    except Exception as e:
        print(f"❌ Ocorreu um erro ao gerar a imagem: {e}")
        return None
