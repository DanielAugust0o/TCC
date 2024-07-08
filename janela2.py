import customtkinter as ctk
from tkinter import *
from tkinter import messagebox
janela = ctk.CTk()


class Application():
    def __init__(self):
        self.janela = janela
        self.tema()
        self.tela()
        self.tela_login()
        janela.mainloop()
    def tema(self):
        # Definindo o tema personalizado
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme('Tema.json')

    def tela(self):
        # Criando a janela principal
        janela.geometry('700x400')
        janela.title('Tela de Login')
        janela.resizable(False, False)
        janela.configure(bg='white')
        janela.iconbitmap('/Users/danielaugusto/PycharmProjects/TCC/ppe1.ico')  # Definindo o ícone da janela

    def tela_login(self):
        # Definindo a cor padrão do App
        cor_rgb = '#343434'

        # Frame para imagem
        frame0 = Frame(master=janela, bg='#1c1c1c', width=350, height=396)
        frame0.pack(side=RIGHT)
        # Frame para os widgets de login
        frame = Frame(master=janela, bg=cor_rgb, width=350, height=396)
        frame.pack(side=LEFT)

        # Carregando e exibindo a imagem
        img = PhotoImage(file='Imagens/ppe1.png')
        label_img = ctk.CTkButton(master=frame0, text='', image=img)
        label_img.configure(text=None, hover=None)
        label_img.place(x=45, y=115)

        label_tt = ctk.CTkLabel(master=frame0, text='Entre em sua conta e tenha \nacesso a plataforma')
        label_tt.configure(font=('Roboto', 24, 'bold'), text_color='#EEAD2D', bg_color='#1c1c1c')
        label_tt.place(x=30, y=40)


        # Label principal da tela de login
        label = ctk.CTkLabel(master=frame, text='Tela de Login')
        label.configure(font=('Roboto', 30, 'bold'))
        label.place(x=70, y=25)

        # Campo de entrada para o usuário
        usuario = ctk.CTkEntry(frame, placeholder_text='Usuário', width=310, height=35)
        usuario.place(x=20, y=80)
        usuario.configure(font=('Roboto', 14))

        # Label informativa abaixo do campo de usuário
        label1 = ctk.CTkLabel(master=frame, text='*Obrigatório preenchimento do campo usuário.', text_color='#EEAD2D')
        label1.place(x=20, y=115)
        label1.configure(font=('Roboto', 10))

        # Campo de entrada para a senha
        senha = ctk.CTkEntry(frame, placeholder_text='Senha', width=310, height=35, show='*')
        senha.place(x=20, y=160)
        senha.configure(font=('Roboto', 14))

        # Label informativa abaixo do campo de senha
        label2 = ctk.CTkLabel(master=frame, text='*Obrigatório preenchimento do campo senha.', text_color='#EEAD2D')
        label2.place(x=20, y=195)
        label2.configure(font=('Roboto', 10))

        # Checkbox "Manter login"
        checkbox = ctk.CTkCheckBox(master=frame, text='Manter login')
        checkbox.place(x=20, y=240)
        checkbox.configure(font=('Roboto', 16))

        def logando():
            msg = messagebox.showinfo(title='Estado de Login', message='Parabéns! Login feito com sucesso.')
            pass
        # Botão de login
        botao_login = ctk.CTkButton(master=frame, text='Login', fg_color='#fcbc1c', hover_color='#FFD700', width=300, command=logando)
        botao_login.place(x=20, y=280)

        def tela_cadastro():
            #Remover tela de login
            frame.pack_forget()

            #Criando tela de cadastro de usuários
            cd_frame = Frame(master=janela, bg=cor_rgb, width=350, height=396)
            cd_frame.pack(side=LEFT)

            # Titulo da janela
            cd_label = ctk.CTkLabel(master=cd_frame, text='Cadastre-se')
            cd_label.configure(font=('Roboto', 30, 'bold'))
            cd_label.place(x=70, y=15)

            span = ctk.CTkLabel(master=cd_frame, text='* Por Favor! Preencha todos campos', text_color='gray')
            span.place(x=25, y=105)
            span.configure(font=('Roboto', 12, 'bold'))

            #Campo de entrada de dados
            usuario = ctk.CTkEntry(cd_frame, placeholder_text='Nome de usuário', width=310, height=35)
            usuario.place(x=20, y=130)
            usuario.configure(font=('Roboto', 14))

            email = ctk.CTkEntry(cd_frame, placeholder_text='E-mail de usuario', width=310, height=35)
            email.place(x=20, y=180)
            email.configure(font=('Roboto', 14))

            senha_usuario = ctk.CTkEntry(cd_frame, placeholder_text='Senha de usuário', width=310, height=35,show='*')
            senha_usuario.place(x=20, y=230)
            senha_usuario.configure(font=('Roboto', 14))

            csenha_usuario = ctk.CTkEntry(cd_frame, placeholder_text='Confirmar senha', width=310, height=35,)
            csenha_usuario.place(x=20, y=280)
            csenha_usuario.configure(font=('Roboto', 14))

            def voltar():
                #Removendo frame de cadastro
                cd_frame.pack_forget()

                # Voltando frame de login
                frame.pack(side=LEFT)

            botao_voltar = ctk.CTkButton(master=cd_frame, text='VOLTAR', fg_color='#FF0000', hover_color='#8B0000', width=145, command=voltar)
            botao_voltar.place(x=20, y=330)

            def cadastrar_usuario():
                msg = messagebox.showinfo(title='Estado do Cadastro', message='Usuário cadastrado com sucesso.')
                pass

            botao_salvar = ctk.CTkButton(master=cd_frame, text='CADASTRAR', fg_color='#4c6c8c', hover_color='#4682B4',width=145, command=cadastrar_usuario)
            botao_salvar.place(x=185, y=330)


        # Label realizar cadastro
        label4 = ctk.CTkLabel(master=frame, text='Não possuí uma conta?')
        label4.configure(font=('Roboto', 12, 'bold'))
        label4.place(x=25, y=335)
        botao_cadastro = ctk.CTkButton(master=frame, text='Cadastre-se', fg_color='#4c6c8c', hover_color='#4682B4',
                                       width=150, command=tela_cadastro)
        botao_cadastro.place(x=170, y=335)



Application()
