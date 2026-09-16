import customtkinter as ctk
from customtkinter import (
    CTk,
    CTkLabel,
    CTkEntry,
    CTkButton,
    CTkFrame,
)
from pathlib import Path
from browser import realizar_login
from browser import buscar_contratos
from browser import processar_contrato

class Interface:

    def __init__(self):
        self.app = CTk()

        self.app.title("Anexos - Contratos por Projeto")
        self.app.geometry("600x400")
        self.criar_componentes()

    def iniciar(self):
        self.app.mainloop()

    def criar_componentes(self):
        #coloque os componentes aqui
        self.fundo_interface = CTkFrame(self.app, width=250)
        self.fundo_interface.grid(row=0, column=1, sticky="ns")
        self.fundo_interface.pack()
        #self.label_projeto = CTkLabel(self.app,text="Número do projeto")
        #self.label_projeto.pack()

    # ignora por enquanto, o botão chamará futuramente   
    def botao_iniciar_processo(numero_projeto):
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






    