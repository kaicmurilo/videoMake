import os
os.environ["TORCH_CUDA_ARCH_LIST"] = "8.9+PTX"
os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
os.environ["TORCH_USE_CUDA_DSA"] = "1"

from diffusers import StableDiffusionPipeline
import torch

CAMINHO_IMAGEM = "./saida.png"  # ajuste se necessário

def gerar_imagem_local(prompt: str) -> str:
    print("⚙️ Gerando imagem localmente com diffusers...")

    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        torch_dtype=torch.float16,
        use_safetensors=True,
        variant="fp16",  # garante compatibilidade
    ).to("cuda")

    pipe.enable_attention_slicing()
    pipe.enable_model_cpu_offload()

    imagem = pipe(prompt, num_inference_steps=20).images[0]
    imagem.save(CAMINHO_IMAGEM)
    print("✅ Imagem gerada localmente.")
    return CAMINHO_IMAGEM
