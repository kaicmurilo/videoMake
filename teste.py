# Importações novas e mais limpas
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel, ImageGenerationResponse
import os

# --- CONFIGURAÇÃO ---
# O código continua pegando o ID do projeto da variável de ambiente
PROJECT_ID = os.getenv("GOOGLEPROJECT") 
LOCATION = "us-central1"
OUTPUT_FILE = "imagem_gerada_google.png"

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

# --- BLOCO DE EXECUÇÃO ---
if __name__ == "__main__":
    if not PROJECT_ID:
        print("🚨 ATENÇÃO: A variável de ambiente 'GOOGLEPROJECT' não está definida.")
    else:
        meu_prompt = "Um carro futurista voando sobre a Ponte Estaiada em São Paulo ao pôr do sol, estilo cyberpunk"
        gerar_imagem_google(meu_prompt)