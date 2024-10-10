from ultralytics import YOLO

# Carregar o modelo
model = YOLO("best4.pt")

# Verificar as classes
class_names = model.names  # Isso retorna uma lista com os nomes das classes
print(class_names)
