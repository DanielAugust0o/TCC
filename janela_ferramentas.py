
import customtkinter as ctk

class janela2(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry('1000x700')
        self.title('Nova Janela')
        self.resizable(False, False)
        self.label = ctk.CTkLabel(self, text="Bem-vindo à nova janela!")
        self.label.pack(pady=20)

if __name__ =='__main__':
    janela_ferramentas = janela2()
    janela_ferramentas.mainloop()
