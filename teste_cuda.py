import torch
print("Versão do PyTorch:", torch.__version__)
print("CUDA disponível:", torch.cuda.is_available())
print("GPU:", torch.cuda.get_device_name(0))
print("Capacidade compute:", torch.cuda.get_device_capability(0))
