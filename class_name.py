from ultralytics import YOLO

# Carregue seu modelo treinado
model = YOLO('best4.pt')  # Substitua pelo caminho do seu modelo

# Carregar o modelo
model = YOLO("best.pt")

# Acessar o nome das classes
class_names = model.names

# Exibir as classes treinadas
print(class_names)
