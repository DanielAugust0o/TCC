import customtkinter as ctk
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2

class JanelaMenu(ctk.CTk):
    def __init__(self, usuario):
        super().__init__()
        self.title("Aplicação")
        self.geometry("1200x600")
        self.usuario = usuario
        self.criar_menu_superior()
        self.resizable(False, False)
        self.video = cv2.VideoCapture(0)

        # Criar o frame inicial com o botão
        self.frame_inicial = ctk.CTkFrame(self, width=1200, height=600, fg_color='#FFFFFF')
        self.frame_inicial.place(x=0, y=0)
        self.btn_iniciar = ctk.CTkButton(self.frame_inicial, text='Iniciar Câmera', font=('Roboto bold', 20), command=self.iniciar_camera)
        self.btn_iniciar.place(relx=0.5, rely=0.5, anchor=CENTER)

    def item1_command(self):
        print("Item 1 selecionado")

    def item2_command(self):
        print("Item 2 selecionado")

    def criar_menu_superior(self):
        # Criar o frame da barra de menu
        self.frame_menu = ctk.CTkFrame(self, width=1200, height=65, fg_color='#4c6c8c')
        self.frame_menu.place(x=0, y=0)

        # Tratando a imagem do logo
        image_path = 'Imagens/capacete.png'
        img = Image.open(image_path)
        # Redimensionando a imagem
        img = img.resize((63, 63), Image.LANCZOS)
        self.logo = ImageTk.PhotoImage(img)

        # Adicionando elementos ao menu
        self.lb_logo = ctk.CTkLabel(self.frame_menu, text='', image=self.logo, fg_color='#4c6c8c')
        self.lb_logo.grid(row=0, column=0, padx=40, pady=1)

        # Adicionando mensagem de boas-vindas
        self.mensagem = ctk.CTkLabel(self.frame_menu, text=f'Olá {self.usuario}', font=('Roboto', 16), text_color='White', fg_color='#4c6c8c')
        self.mensagem.grid(row=0, column=1, padx=900, pady=1)

        # Configurando frame da seleção de câmera
        self.frame_camera = ctk.CTkFrame(self, width=300, height=400)
        self.frame_camera.place(x=20, y=135)

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
        self.frame_bd_imagem.place(x=40, y=485)
        self.btn_bd_imagem = ctk.CTkButton(self.frame_bd_imagem, width=250, height=40, text='Banco de Imagens'.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20, fg_color='#EEAD2D', command=self.pasta_imagens)
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

        self.btn_detectar = ctk.CTkButton(self.frame_deteccao, width=250, height=40, text='Detectar'.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20, fg_color='#EEAD2D')
        self.btn_detectar.grid(row=6, column=0, padx=10, pady=(20, 10))

    def iniciar_camera(self):
        self.frame_inicial.place_forget()  # Esconder o frame inicial
        self.update_frame()  # Iniciar a captura de vídeo

    def update_frame(self):
        ret, frame = self.video.read()
        if ret:
            height, width = frame.shape[:2]
            frame_aspect_ratio = width / height
            label_width = 640
            label_height = int(label_width / frame_aspect_ratio)

            if label_height > 480:
                label_height = 480
                label_width = int(label_height * frame_aspect_ratio)
            frame = cv2.resize(frame, (label_width, label_height))
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=img)
            self.lb_video.configure(image=imgtk)
            self.lb_video.image = imgtk

        self.lb_video.after(10, self.update_frame)

    def pasta_imagens(self):
        diretorio = filedialog.askdirectory(initialdir="/Users/danielaugusto/PycharmProjects/TCC/Imagens")
        if diretorio:
            print(f"Diretório selecionado: {diretorio}")


if __name__ == "__main__":
    usuario_logado = "Usuário"  # Passe o nome de usuário logado aqui
    app = JanelaMenu(usuario_logado)
    app.mainloop()
