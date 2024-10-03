from ultralytics import YOLO
import cv2
import os
import time
import torch

USERNAME = 'admin'
PASSWORD = 'daniel775'
IP = '192.168.0.108'

# Verifica se a GPU está disponível
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Usando o dispositivo: {device}")

# Inicializa o modelo YOLO no dispositivo correto
model = YOLO("best1.pt").to(device)

# Configurações de ambiente para o OpenCV utilizar o FFmpeg
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

# URL corrigida para RTSP
URL = f'rtsp://{USERNAME}:{PASSWORD}@{IP}/onvif1'
print(f'Conectado com: {URL}')

# Inicializa a captura de vídeo RTSP
video = cv2.VideoCapture(URL, cv2.CAP_FFMPEG)
if not video.isOpened():
    print('Erro ao abrir a câmera RTSP')
else:
    print('Câmera RTSP conectada com sucesso')

# Define o tamanho da imagem (resolução menor para melhor desempenho)
video.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Você pode ajustar isso conforme necessário
video.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Limita a taxa de quadros (FPS)
video.set(cv2.CAP_PROP_FPS, 10)

# Loop para capturar frames e realizar predições
frame_skip = 5  # Processar a cada 5 frames para reduzir o uso de CPU
frame_count = 0

while True:
    ret, frame = video.read()

    if not ret:
        print('Erro ao capturar frame')
        break

    frame_count += 1

    # Só processa o frame a cada 5 frames para melhorar o desempenho
    if frame_count % frame_skip == 0:
        start_time = time.time()

        # Redimensiona o frame para 640x640 antes de convertê-lo para tensor
        frame_resized = cv2.resize(frame, (640, 640))

        # Converte o frame redimensionado para tensor e move para a GPU
        frame_tensor = torch.from_numpy(frame_resized).permute(2, 0, 1).unsqueeze(0).to(device).float() / 255.0  # Transpor e normalizar

        # Faz predição no frame capturado
        results = model.predict(source=frame_tensor, conf=0.5, device=device, show=True)

        end_time = time.time()
        print(f'Tempo para predição: {end_time - start_time:.2f} segundos')

    # Pressione 'q' para sair
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera os recursos
video.release()
cv2.destroyAllWindows()
