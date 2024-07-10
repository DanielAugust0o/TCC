import customtkinter as ctk
from tkinter import *
from PIL import Image, ImageTk


class JanelaMenu(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Aplicação")
        self.geometry("1200x600")
        self.criar_menu_superior()

    def item1_command(self):
        print("Item 1 selecionado")

    def item2_command(self):
        print("Item 2 selecionado")

    def criar_menu_superior(self):
        # criar o frame da barra de menu
        self.frame_login = ctk.CTkFrame(self, width=1200, height=65, fg_color='#4c6c8c')
        self.frame_login.place(x=0, y=0)


        #tratando a Imagem Logo
        image_path = 'Imagens/capacete.png'
        img = Image.open(image_path)
        #redimensionando a imagem
        img = img.resize((63,63), Image.LANCZOS)
        self.logo = ImageTk.PhotoImage(img)

        #adicionando elementos ao menu
        self.lb_logo = ctk.CTkLabel(self, text=None, image=self.logo, fg_color='#4c6c8c')
        self.lb_logo.grid(row=1, column=0, padx=40, pady=1)

        #adicionando mensagem de boas vindas
        self.mensagem = ctk.CTkLabel(self, text=f'Olá{self.username_cadastro}')


if __name__ == "__main__":
    app = JanelaMenu()
    app.mainloop()
