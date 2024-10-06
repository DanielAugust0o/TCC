import os
import time
import cv2
import customtkinter as ctk
from tkinter import *
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
TOKEN = '7631292504:AAE832UkHj2scbakf6XG5aNMG2L1l5pQMfk'
CHAT_ID = '1271362249'  #  # Substitua pelo chat ID do grupo ou usuário

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
        self.model = YOLO("best4.pt").to(device)  # Substitua pelo caminho do seu modelo

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

        self.btn_camera1 = ctk.CTkButton(self.frame_camera, width=280, height=40, text='Camera 1'.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20)
        self.btn_camera1.grid(row=2, column=0, padx=10, pady=(20, 10))

        self.btn_camera2 = ctk.CTkButton(self.frame_camera, width=280, height=40, text='Camera 2'.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20)
        self.btn_camera2.grid(row=3, column=0, padx=10, pady=(20, 10))

        self.btn_camera3 = ctk.CTkButton(self.frame_camera, width=280, height=40, text='Camera 3'.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20)
        self.btn_camera3.grid(row=4, column=0, padx=10, pady=(20, 10))

        self.btn_camera4 = ctk.CTkButton(self.frame_camera, width=280, height=40, text='Camera 4'.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20)
        self.btn_camera4.grid(row=5, column=0, padx=10, pady=(20, 10))

        # Frame banco de imagens
        self.frame_bd_imagem = ctk.CTkFrame(self, fg_color='#242424')
        self.frame_bd_imagem.place(x=40, y=450)
        self.btn_bd_imagem = ctk.CTkButton(self.frame_bd_imagem, width=250, height=40, text='Banco de Imagens'.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20, fg_color='#EEAD2D', hover_color='#f4a42c', command=self.pasta_imagens)
        self.btn_bd_imagem.grid(row=0, column=0, padx=10, pady=(20, 10))

        # Frame para exibir o vídeo da câmera
        self.frame_video = ctk.CTkFrame(self, width=500, height=500, fg_color='#242424')
        self.frame_video.place(x=343, y=65)
        self.lb_video = ctk.CTkLabel(self.frame_video, text='', width=640, height=480)
        self.lb_video.place(relx=0.5, rely=0.5, anchor=CENTER)

        # Configurando frame da IA
        self.frame_deteccao = ctk.CTkFrame(self, width=300, height=400)
        self.frame_deteccao.place(x=865, y=135)

        self.titulo = ctk.CTkLabel(self.frame_deteccao, text='Identificar:', font=('Roboto', 24, 'bold'))
        self.titulo.grid(row=1, column=0, pady=(20, 0), padx=20, sticky="n")

        self.check_capacete = ctk.CTkCheckBox(self.frame_deteccao, width=300, text='Capacete'.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20)
        self.check_capacete.grid(row=2, column=0, padx=10, pady=(20, 10))

        self.check_luvas = ctk.CTkCheckBox(self.frame_deteccao, width=300, text='luvas'.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20)
        self.check_luvas.grid(row=3, column=0, padx=10, pady=(20, 10))

        self.check_botas = ctk.CTkCheckBox(self.frame_deteccao, width=300, text='botas'.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20)
        self.check_botas.grid(row=4, column=0, padx=10, pady=(20, 10))

        self.check_protetor_auricular = ctk.CTkCheckBox(self.frame_deteccao, width=300, text='protetor Auricular'.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20)
        self.check_protetor_auricular.grid(row=5, column=0, padx=10, pady=(20, 10))

        self.btn_detectar = ctk.CTkButton(self.frame_deteccao, width=250, height=40, text='Detectar'.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20, fg_color='#EEAD2D', hover_color='#f4a42c')
        self.btn_detectar.grid(row=6, column=0, padx=10, pady=(20, 10))

    def process_frame(self):
        while self.running:
            try:
                ret, frame = self.video.read()  # Captura o frame atual
                if ret:
                    # Aplica o modelo YOLO ao frame
                    results = self.model(frame)  # Realiza a detecção

                    # Lista para armazenar as classes detectadas
                    detected_items = []

                    for result in results:  # Itera sobre cada detecção
                        for box in result.boxes:  # Para cada boxe detectado
                            cls = int(box.cls)  # Pega a classe do objeto detectado
                            detected_items.append(cls)  # Armazena na lista

                    # Verifique quais itens de EPI foram detectados
                    missing_items = []
                    if 0 not in detected_items:  # Classe 0 = botas
                        missing_items.append('Botas')
                    if 1 not in detected_items:  # Classe 1 = óculos
                        missing_items.append('Óculos de Proteção')
                    if 2 not in detected_items:  # Classe 2 = luvas
                        missing_items.append('Luvas')
                    if 3 not in detected_items:  # Classe 3 = capacete
                        missing_items.append('Capacete')
                    if 4 not in detected_items:  # Classe 4 = pessoa
                        missing_items.append('Pessoa')
                    if 5 not in detected_items:  # Classe 5 = colete
                        missing_items.append('Colete')

                    # Se houver itens faltando, envie um alerta pelo Telegram
                    if missing_items:
                        try:
                            send_telegram_message(
                                f"Alerta: Os seguintes itens de EPI não foram identificados: {', '.join(missing_items)}"
                            )
                        except Exception as e:
                            print(f"Erro ao enviar mensagem pelo Telegram: {e}")

                    # Desenha as detecções no frame
                    annotated_frame = results[0].plot()  # Desenha as detecções no frame

                    if not self.frame_queue.full():
                        if not self.frame_queue.empty():
                            self.frame_queue.get_nowait()  # Descartar frame antigo
                        self.frame_queue.put(annotated_frame)

            except Exception as e:
                print(f"Erro durante o processamento do frame: {e}")
            time.sleep(0.01)  # Pausa para não sobrecarregar a CPU

    def update_frame(self):
        if not self.frame_queue.empty():
            self.frame = self.frame_queue.get()
            frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

            # Redimensiona a imagem mantendo a proporção
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

        # Atualiza o frame a cada 15ms
        self.after(15, self.update_frame)

    def pasta_imagens(self):
        diretorio = filedialog.askdirectory(initialdir="/Users/danielaugusto/PycharmProjects/TCC/Imagens")
        if diretorio:
            print(f"Diretório selecionado: {diretorio}")

    def on_closing(self):
        # Encerra a captura de vídeo e a thread de processamento
        self.running = False
        self.video.release()
        self.processing_thread.join()  # Aguardando a thread de processamento terminar
        cv2.destroyAllWindows()
        self.destroy()


if __name__ == "__main__":
    usuario_logado = "Usuário"  # Passe o nome de usuário logado aqui
    app = JanelaMenu(usuario_logado)
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
    bot.polling()
