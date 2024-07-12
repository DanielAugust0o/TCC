import customtkinter as ctk
from tkinter import *
from PIL import Image, ImageTk

class JanelaMenu(ctk.CTk):
    def __init__(self, usuario):
        super().__init__()
        self.title("Aplicação")
        self.geometry("1200x600")
        self.usuario = usuario
        self.criar_menu_superior()
        self.resizable(False, False)

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


        # configurando label camera
        self.frame_camera = ctk.CTkFrame(self, width=300, height=400)
        self.frame_camera.place(x=30, y=130)

        self.titulo = ctk.CTkLabel(self.frame_camera, text='Selecione a Câmera:', font=('Roboto', 22, 'bold'))
        self.titulo.grid(row=1, column=0, padx=10, pady=(20, 10))

        self.btn_camera1 = ctk.CTkButton(self.frame_camera, width=300, text='Camera 1'.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20)
        self.btn_camera1.grid(row=2, column=0, padx=10, pady=(20, 10))

        self.btn_camera2 = ctk.CTkButton(self.frame_camera, width=300, text='Camera 2'.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20)
        self.btn_camera2.grid(row=3, column=0, padx=10, pady=(20, 10))

        self.btn_camera3 = ctk.CTkButton(self.frame_camera, width=300, text='Camera 3'.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20)
        self.btn_camera3.grid(row=4, column=0, padx=10, pady=(20, 10))

        self.btn_camera4 = ctk.CTkButton(self.frame_camera, width=300, text='Camera 4'.upper(), font=('Roboto bold', 16, 'bold'), corner_radius=20)
        self.btn_camera4.grid(row=5, column=0, padx=10, pady=(20, 10))




if __name__ == "__main__":
    usuario_logado = "Usuário"  # Passe o nome de usuário logado aqui
    app = JanelaMenu(usuario_logado)
    app.mainloop()
