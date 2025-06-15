from diffusers import StableDiffusionPipeline
import torch


def gerar_imagem_huggingface(prompt):
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5",
        safety_checker=None,
        torch_dtype=torch.float16
    ).to("cuda")

    pipe.enable_attention_slicing()

    with torch.autocast("cuda"):
        image = pipe(prompt).images[0]

    if image is not None:
        image.save("saida.png")
        print("✅ Imagem gerada com sucesso.")
    else:
        print("❌ Imagem inválida.")
