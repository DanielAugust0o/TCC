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
from datetime import datetime
import matplotlib.pyplot as plt



USERNAME = 'admin'
PASSWORD = 'daniel775'
IP = '192.168.0.106'

# Configurações do Telegram
TOKEN = '7552093490:AAG_7ho97BYEQjoZ67BKeNTnIgX7VKKFcBQ'
CHAT_ID = '1184444451'

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
        self.model = YOLO("best5.pt").to(device)

        # Configurações de ambiente para o OpenCV utilizar o FFmpeg
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

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
        self.detection_active = False  # Controle de detecção
        self.frame_queue = queue.Queue(maxsize=2)
        self.last_alert_time = 0  # Controle de tempo do alerta

        # Inicia o processamento de frames em uma thread separada
        self.processing_thread = threading.Thread(target=self.process_frame, daemon=True)
        self.processing_thread.start()

        # Atualiza o frame
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

        # elementos do menu
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

        # Configurando Frame de identificação
        self.frame_deteccao = ctk.CTkFrame(self, width=300, height=550)
        self.frame_deteccao.place(x=865, y=135)

        self.titulo = ctk.CTkLabel(self.frame_deteccao, text='Identificar:', font=('Roboto', 24, 'bold'))
        self.titulo.grid(row=1, column=0, pady=(20, 0), padx=20, sticky="n")

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

        self.btn_detectar = ctk.CTkButton(self.frame_deteccao, width=250, height=40, text='Detectar'.upper(), font=('Roboto', 16, 'bold'), corner_radius=20, fg_color='#EEAD2D', hover_color='#f4a42c', command=self.toggle_detection)
        self.btn_detectar.grid(row=7, column=0, padx=10, pady=(30, 10))

    def toggle_detection(self):
        self.detection_active = not self.detection_active
        if self.detection_active:
            self.btn_detectar.configure(text='Parar Detecção')
            # Reiniciar a captura de vídeo para evitar travamentos, se necessário
            # self.video.release()
            # time.sleep(0.5)
            # self.video = cv2.VideoCapture(0)
        else:
            self.btn_detectar.configure(text='Detectar')
            # Se desejar parar completamente a captura, descomente a linha abaixo
            # self.video.release()

    # Método para verificar os checkboxes selecionados
    # Método para verificar os checkboxes selecionados
    def get_selected_items(self):
        selected_items = []
        if self.check_botas.get() == 1:
            selected_items.append(0)  # 'Botas' corresponde ao índice 0
        if self.check_oculos.get() == 1:
            selected_items.append(1)  # 'Óculos de Proteção' corresponde ao índice 1
        if self.check_luvas.get() == 1:
            selected_items.append(2)  # 'Luvas' corresponde ao índice 2
        if self.check_capacete.get() == 1:
            selected_items.append(3)  # 'Capacete' corresponde ao índice 3
        if self.check_colete.get() == 1:
            selected_items.append(5)  # 'Colete' corresponde ao índice 5
        return selected_items

    # Função auxiliar para mapear o índice para o nome do item
    def get_item_name(self, item_index):
        item_map = {
            0: 'Botas',
            1: 'Óculos de Proteção',
            2: 'Luvas',
            3: 'Capacete',
            5: 'Colete'
        }
        return item_map.get(item_index, 'Desconhecido')

    # Método para verificar itens faltando considerando os itens selecionados
    def check_missing_items(self, detected_items, selected_items):
        missing_items = []

        # Verifica os itens selecionados e checa se foram detectados
        for item_index in selected_items:
            if item_index not in detected_items:  # Se não foi detectado, é considerado "faltante"
                item_name = self.get_item_name(item_index)
                missing_items.append(item_name)

        return missing_items

    # Método para processar o frame e verificar apenas os itens selecionados
    import os
    import cv2
    from datetime import datetime

    def process_frame(self):
        while self.running:
            try:
                ret, frame = self.video.read()
                if ret:
                    if self.detection_active:
                        results = self.model(frame)
                        # Extrai as classes detectadas no frame
                        detected_items = [int(box.cls) for result in results for box in result.boxes]
                        selected_items = self.get_selected_items()

                        print(
                            f"Itens detectados: {detected_items}")  # Adicionando log para verificar o que está sendo detectado
                        print(f"Itens selecionados: {selected_items}")  # Log dos itens que foram selecionados

                        # A pessoa (classe 4) sempre deve ser detectada
                        if 4 in detected_items:
                            # Verifica quais itens selecionados não foram detectados
                            missing_items = self.check_missing_items(detected_items, selected_items)

                            if missing_items and (time.time() - self.last_alert_time > 10):
                                # Envia a mensagem no Telegram
                                send_telegram_message(
                                    f"Atenção: Colaborador não está usando: {', '.join(missing_items)}")

                                # Salva o frame com itens faltando
                                self.save_frame_with_missing_items(frame)

                                self.last_alert_time = time.time()
                            else:
                                print("Nenhum item faltando detectado.")
                        else:
                            print("Nenhuma pessoa detectada.")

                        # Processa o frame com as detecções e coloca na fila
                        annotated_frame = results[0].plot()
                        if not self.frame_queue.full():
                            if not self.frame_queue.empty():
                                self.frame_queue.get_nowait()
                            self.frame_queue.put(annotated_frame)
                    else:
                        # Exibe o frame sem detecção
                        if not self.frame_queue.full():
                            if not self.frame_queue.empty():
                                self.frame_queue.get_nowait()
                            self.frame_queue.put(frame)
                else:
                    time.sleep(0.1)
            except Exception as e:
                print(f"Erro durante o processamento do frame: {e}")

    # Função para salvar o frame quando itens estão faltando
    def save_frame_with_missing_items(self, frame):
        # Definir o diretório onde as imagens serão salvas
        image_directory = "ImagensCapturadas"

        # Criar o diretório se ele não existir
        if not os.path.exists(image_directory):
            os.makedirs(image_directory)

        # Criar um nome único para a imagem com base na data e hora atuais
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"{image_directory}/Frame_{timestamp}.jpg"

        # Salvar o frame como uma imagem
        cv2.imwrite(image_filename, frame)

        print(f"Imagem salva: {image_filename}")

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
        diretorio = filedialog.askdirectory(initialdir="/Users/danielaugusto/PycharmProjects/TCC/ImagensCapturadas")
        if diretorio:
            print(f"Diretório selecionado: {diretorio}")

            # Lista os arquivos no diretório selecionado
            arquivos = os.listdir(diretorio)

            # Filtra apenas as imagens
            imagens = [f for f in arquivos if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

            for imagem in imagens:
                caminho_imagem = os.path.join(diretorio, imagem)
                print(f"Abrindo imagem: {caminho_imagem}")

                # Abre e exibe a imagem
                img = Image.open(caminho_imagem)
                plt.imshow(img)
                plt.axis('off')  # Oculta os eixos
                plt.show()

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
