import os
import time
import cv2
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk
import threading
import queue
from ultralytics import YOLO
import torch
import telebot

USERNAME = 'admin'
PASSWORD = 'daniel775'
IP = '192.168.0.106'

# Configurações do Telegram
TOKEN = '7552093490:AAG_7ho97BYEQjoZ67BKeNTnIgX7VKKFcBQ'
CHAT_ID = '1184444451'  # Substitua pelo chat ID do grupo ou usuário

bot = telebot.TeleBot(token=TOKEN)

def send_telegram_message(text):
    try:
        bot.send_message(chat_id=CHAT_ID, text=text)
        print("Mensagem enviada com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar mensagem pelo Telegram: {e}")

class JanelaMenu(ctk.CTk):
    def __init__(self, usuario):
        super().__init__()
        self.title("Aplicação")
        self.geometry("1200x600")
        self.usuario = usuario
        self.criar_menu_superior()
        self.resizable(False, False)

        # Inicializa o modelo YOLO
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = YOLO("best4.pt").to(device)

        # Configurações de ambiente para o OpenCV utilizar o FFmpeg
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

        # URL corrigida para rtsp
        self.URL = f'rtsp://{USERNAME}:{PASSWORD}@{IP}/onvif1'
        print(f'Conectado com: {self.URL}')

        # Inicializa a captura de vídeo RTSP
        self.video = cv2.VideoCapture(0)
        self.video.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        if not self.video.isOpened():
            print('Erro ao abrir a câmera RTSP')
        else:
            print('Câmera RTSP conectada com sucesso')

        self.frame = None
        self.results = None
        self.running = True
        self.frame_queue = queue.Queue(maxsize=2)
        self.last_alert_time = 0  # Controle de tempo do alerta
        self.detection_active = False  # Controle para iniciar a detecção

        # Inicia o processamento de frames em uma thread separada
        self.processing_thread = threading.Thread(target=self.process_frame, daemon=True)
        self.processing_thread.start()

        # Atualiza o frame com segurança
        self.update_frame()

    def criar_menu_superior(self):
        # Criar o frame da barra de menu
        self.frame_menu = ctk.CTkFrame(self, width=1200, height=65, fg_color='#4c6c8c')
        self.frame_menu.place(x=0, y=0)

        # Tratando a imagem do logo
        image_path = 'Imagens/capacete.png'
        img = Image.open(image_path)
        img = img.resize((63, 63), Image.LANCZOS)
        self.logo = ImageTk.PhotoImage(img)

        # Adicionando elementos ao menu
        self.lb_logo = ctk.CTkLabel(self.frame_menu, text='', image=self.logo, fg_color='#4c6c8c')
        self.lb_logo.grid(row=0, column=0, padx=40, pady=1)

        self.mensagem = ctk.CTkLabel(self.frame_menu, text=f'Olá {self.usuario}', font=('Roboto', 16), text_color='White', fg_color='#4c6c8c')
        self.mensagem.grid(row=0, column=1, padx=900, pady=1)

        # Configurando frame da seleção de câmera
        self.frame_camera = ctk.CTkFrame(self, width=300, height=600)
        self.frame_camera.place(x=20, y=90)

        self.titulo = ctk.CTkLabel(self.frame_camera, text='Selecione o Setor:', font=('Roboto', 22, 'bold'))
        self.titulo.grid(row=1, column=0, padx=10, pady=(20, 10))

        # Botões da câmera
        for i in range(1, 5):
            btn_camera = ctk.CTkButton(self.frame_camera, width=280, height=40, text=f'Camera {i}'.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20)
            btn_camera.grid(row=i + 1, column=0, padx=10, pady=(20, 10))

        # Frame banco de imagens
        self.frame_bd_imagem = ctk.CTkFrame(self, fg_color='#242424')
        self.frame_bd_imagem.place(x=40, y=450)
        self.btn_bd_imagem = ctk.CTkButton(self.frame_bd_imagem, width=250, height=40, text='Banco de Imagens'.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20, fg_color='#EEAD2D', hover_color='#f4a42c', command=self.pasta_imagens)
        self.btn_bd_imagem.grid(row=0, column=0, padx=10, pady=(20, 10))

        # Frame para exibir o vídeo da câmera
        self.frame_video = ctk.CTkFrame(self, width=500, height=500, fg_color='#242424')
        self.frame_video.place(x=343, y=65)
        self.lb_video = ctk.CTkLabel(self.frame_video, text='', width=640, height=480)
        self.lb_video.place(relx=0.5, rely=0.5, anchor='center')
        self.frame_deteccao = ctk.CTkFrame(self, width=300, height=550)
        self.frame_deteccao.place(x=865, y=135)

        self.titulo = ctk.CTkLabel(self.frame_deteccao, text='Identificar:', font=('Roboto', 24, 'bold'))
        self.titulo.grid(row=1, column=0, pady=(20, 0), padx=20, sticky="n")

        # Configurando Frame de identificação
        self.check_botas = ctk.CTkCheckBox(self.frame_deteccao, width=300, text='Botas'.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20)
        self.check_botas.grid(row=2, column=0, padx=10, pady=(20, 10))

        self.check_oculos = ctk.CTkCheckBox(self.frame_deteccao, width=300, text='Óculos de Proteção'.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20)
        self.check_oculos.grid(row=3, column=0, padx=10, pady=(20, 10))

        self.check_luvas = ctk.CTkCheckBox(self.frame_deteccao, width=300, text='Luvas'.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20)
        self.check_luvas.grid(row=4, column=0, padx=10, pady=(20, 10))

        self.check_capacete = ctk.CTkCheckBox(self.frame_deteccao, width=300, text='Capacete'.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20)
        self.check_capacete.grid(row=5, column=0, padx=10, pady=(20, 10))

        self.check_colete = ctk.CTkCheckBox(self.frame_deteccao, width=300, text='Colete'.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20)
        self.check_colete.grid(row=6, column=0, padx=10, pady=(20, 10))

        # Botão para iniciar a detecção
        self.btn_detectar = ctk.CTkButton(self.frame_deteccao, width=250, height=40, text='Detectar'.upper(), font=('Roboto', 16, 'bold'), corner_radius=20, fg_color='#EEAD2D', hover_color='#f4a42c', command=self.iniciar_deteccao)
        self.btn_detectar.grid(row=7, column=0, padx=10, pady=(30, 10))

    def iniciar_deteccao(self):
        """Função chamada quando o botão 'Detectar' é pressionado."""
        self.detection_active = True  # Ativa a detecção

    def process_frame(self):
        """Processa os frames da câmera e realiza a detecção."""
        while self.running:
            try:
                ret, frame = self.video.read()
                if not ret:
                    print("Falha ao capturar o frame.")
                    continue

                if self.detection_active:  # Realiza a detecção apenas se estiver ativa
                    # Detecção de objetos usando YOLO
                    results = self.model(frame, conf=0.5, max_det=5)

                    # Identifica as classes detectadas
                    detected_items = [int(result.boxes.cls.cpu().numpy()[0]) for result in results]

                    # Verifica se há EPIs faltando e envia mensagem para o Telegram
                    missing_items = self.check_missing_items(detected_items)
                    if missing_items:
                        current_time = time.time()
                        if current_time - self.last_alert_time > 60:  # 60 segundos entre alertas
                            send_telegram_message(f"Atenção! Os seguintes EPIs estão faltando: {missing_items}")
                            self.last_alert_time = current_time

                # Reduz o tamanho do frame para 640x480 para exibir na interface
                frame_resized = cv2.resize(frame, (640, 480))

                # Converte o frame para RGB para o tkinter exibir
                frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

                # Converte o frame em imagem PIL
                frame_pil = Image.fromarray(frame_rgb)
                frame_tk = ImageTk.PhotoImage(frame_pil)

                # Coloca a imagem no label do vídeo
                self.lb_video.imgtk = frame_tk
                self.lb_video.configure(image=frame_tk)

                # Aguarda um curto período antes de processar o próximo frame
                time.sleep(0.03)

            except Exception as e:
                print(f"Erro ao processar frame: {e}")

    def get_selected_items(self):
        selected_items = []
        if self.check_botas.get():
            selected_items.append(0)  # Classe 0: boots
        if self.check_oculos.get():
            selected_items.append(1)  # Classe 1: glasses
        if self.check_luvas.get():
            selected_items.append(2)  # Classe 2: gloves
        if self.check_capacete.get():
            selected_items.append(3)  # Classe 3: helmet
        if self.check_colete.get():
            selected_items.append(5)  # Classe 5: vest
        return selected_items

    def check_missing_items(self, detected_items):
        expected_items = self.get_selected_items()
        missing_items = [item for item in expected_items if item not in detected_items]

        # Mapear os números das classes para os nomes dos itens
        item_names = {0: 'Botas', 1: 'Óculos', 2: 'Luvas', 3: 'Capacete', 5: 'Colete'}
        missing_item_names = [item_names[item] for item in missing_items]

        return missing_item_names

    def update_frame(self):
        if not self.frame_queue.empty():
            frame = self.frame_queue.get()
            self.lb_video.configure(image=frame)
            self.lb_video.image = frame

        self.after(30, self.update_frame)

    def pasta_imagens(self):
        filedialog.askdirectory()

    def close(self):
        self.running = False
        self.video.release()
        self.destroy()

if __name__ == "__main__":
    app = JanelaMenu(usuario="Admin")
    app.protocol("WM_DELETE_WINDOW", app.close)
    app.mainloop()
