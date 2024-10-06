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

        # Configurando frame da IA
        self.frame_deteccao = ctk.CTkFrame(self, width=300, height=400)
        self.frame_deteccao.place(x=865, y=135)

        self.titulo = ctk.CTkLabel(self.frame_deteccao, text='Identificar:', font=('Roboto', 24, 'bold'))
        self.titulo.grid(row=1, column=0, pady=(20, 0), padx=20, sticky="n")

        # Checkboxes para detecção
        for idx, text in enumerate(['Capacete', 'Luvas', 'Botas', 'Protetor Auricular']):
            check_box = ctk.CTkCheckBox(self.frame_deteccao, width=300, text=text.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20)
            check_box.grid(row=idx + 2, column=0, padx=10, pady=(20, 10))

        self.btn_detectar = ctk.CTkButton(self.frame_deteccao, width=250, height=40, text='Detectar'.upper(), font=('Roboto', 16, 'bold'), corner_radius=20, fg_color='#EEAD2D', hover_color='#f4a42c')
        self.btn_detectar.grid(row=6, column=0, padx=10, pady=(20, 10))

    def process_frame(self):
        while self.running:
            try:
                ret, frame = self.video.read()
                if ret:
                    results = self.model(frame)
                    detected_items = [int(box.cls) for result in results for box in result.boxes]

                    # Verificar itens faltando
                    missing_items = self.check_missing_items(detected_items)
                    if missing_items and (time.time() - self.last_alert_time > 10):
                        send_telegram_message(f"Atenção Colaborador não está usando: {', '.join(missing_items)}")
                        self.last_alert_time = time.time()

                    annotated_frame = results[0].plot()
                    if not self.frame_queue.full():
                        if not self.frame_queue.empty():
                            self.frame_queue.get_nowait()
                        self.frame_queue.put(annotated_frame)

            except Exception as e:
                print(f"Erro durante o processamento do frame: {e}")

    def check_missing_items(self, detected_items):
        missing_items = []
        if 0 not in detected_items: missing_items.append('Botas')
        if 1 not in detected_items: missing_items.append('Óculos de Proteção')
        if 2 not in detected_items: missing_items.append('Luvas')
        if 3 not in detected_items: missing_items.append('Capacete')
        if 5 not in detected_items: missing_items.append('Colete')
        return missing_items

    def update_frame(self):
        if not self.frame_queue.empty():
            self.frame = self.frame_queue.get()
            frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

            img = Image.fromarray(frame_rgb)
            img_ratio = img.width / img.height
            label_ratio = self.lb_video.winfo_width() / self.lb_video.winfo_height()

            if img_ratio > label_ratio:
                new_width = self.lb_video.winfo_width()
                new_height = int(new_width / img_ratio)
            else:
                new_height = self.lb_video.winfo_height()
                new_width = int(new_height * img_ratio)

            img = img.resize((new_width, new_height), Image.LANCZOS)
            imgtk = ImageTk.PhotoImage(image=img)

            self.lb_video.configure(image=imgtk)
            self.lb_video.image = imgtk

        self.after(15, self.update_frame)

    def pasta_imagens(self):
        diretorio = filedialog.askdirectory(initialdir="/Users/danielaugusto/PycharmProjects/TCC/Imagens")
        if diretorio:
            print(f"Diretório selecionado: {diretorio}")

    def on_closing(self):
        self.running = False
        self.video.release()
        self.processing_thread.join()
        cv2.destroyAllWindows()
        self.destroy()

if __name__ == "__main__":
    usuario_logado = "Usuário"
    app = JanelaMenu(usuario_logado)
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
