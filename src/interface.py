from tkinter import messagebox
from customtkinter import (
    CTk,
    CTkLabel,
    CTkEntry,
    CTkButton,
    CTkFrame,
    set_appearance_mode,
    CTkFont
)
from pathlib import Path
from browser import realizar_login
from browser import buscar_contratos
from browser import processar_contrato

class Interface:

    def __init__(self):
        self.app = CTk()
        set_appearance_mode("Dark")
        self.app.title("Anexos - Contratos por Projeto")
        self.app.geometry("600x400")
        self.app.resizable(False, False)
        self.criar_componentes()
        self.numero_projeto = None

    def iniciar(self):
        self.app.mainloop()



#função 
    def criar_componentes(self):
        #coloque os componentes aqui
        #criando frame fundo do projeto 1
        self.Frame_fundoProjeto1 = CTkFrame(self.app, width=250,)
        self.Frame_fundoProjeto1.grid(row=0, column=1, sticky="ns")
        self.Frame_fundoProjeto1.pack(pady=(20, 10), padx=(2, 2))

        #criando texto do numero do projeto
        self.label_Nprojeto = CTkLabel(self.Frame_fundoProjeto1,
                                      text="Anexos - Contratos por Projeto",
                                      font=CTkFont(size=20, weight="bold"))
        self.label_Nprojeto.pack(pady=(10, 10), padx=(20, 20))

        #criando canpo para digitar o numero do projeto
        self.campo_N_projeto = CTkEntry(self.app, placeholder_text="Digite o numero do projeto", width=300)

        self.campo_N_projeto.pack(pady=(90,10))

        #criando botao para conferir o numero do projeto
        self.botao_conferir_N_projeto = CTkButton(self.app,
                                                  text="Conferir",
                                                  command=self.botao_conferir_NP)
        self.botao_conferir_N_projeto.pack(pady=(10,10))





    #função botão conferir N projeto
    def botao_conferir_NP(self):
        N_projeto = self.campo_N_projeto.get()
        print(N_projeto)
        print(type(N_projeto))
        mensagemErro = "Erro no valor inserido! Por favor escreva apenas números."
        try:
            N_projeto = int(N_projeto)
            #checa se o n do projeto e uma variavel do tipo "int"
            self.numero_projeto = N_projeto 
            print("foi")
        except:
            messagebox.showinfo(title="ERRO", message=mensagemErro)
            print(N_projeto)
        self.botao_iniciar_processo()

    # ignora por enquanto, o botão chamará futuramente   
    def botao_iniciar_processo(self):
        numero_projeto = self.numero_projeto
        driver = realizar_login()
        resultados = buscar_contratos(driver,numero_projeto)
        
        #Download de anexos cada contrato
        for item in resultados:
            print(f"Contrato: {item['contrato']}")
            print(f"Projeto: {item['projeto']}")
            print(f"Status: {item['status']}")
            print(f"Link contrato: {item['link']}")
            processar_contrato(driver,item,numero_projeto)
    
    
            print("-" * 50)






    