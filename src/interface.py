from logging import root
from tkinter import filedialog, messagebox
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
import sys
from browser import realizar_login
from browser import buscar_contratos
from browser import processar_contrato





class InterfaceAutomacao:

    


    def __init__(self):
        self.app = CTk()

        set_appearance_mode("Dark")

        self.app.title("Anexos - Contratos por Projeto")
        self.app.geometry("600x400")
        self.app.resizable(False, False)

        # Caminho do ícone
        base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
        self.icon = base_dir / "icon" / "logo.ico"

        # Dados da aplicação
        self.numero_projeto = None
        self.diretorio = None

        # Define o ícone da janela
        self.app.iconbitmap(str(self.icon))

        # Cria os componentes
        self.criar_componentes()

    def iniciar(self):
        self.app.mainloop()

    def definir_icone(self, caminho_icone):
        self.icon = caminho_icone


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
                                                  text="Buscar",
                                                  command=self.botao_conferir_Projeto)
        self.botao_conferir_N_projeto.pack(pady=(10,10))

        self.label_status = CTkLabel(self.app, text="Aguardando início.", wraplength=550)
        self.label_status.pack(pady=(10, 10))

    


    


    def selecionar_diretorio(self):
        diretorio = filedialog.askdirectory(
            title="Selecione o diretório"
        )

        if diretorio:
            self.diretorio = Path(diretorio)
        else:
            self.diretorio = None







    #função botão conferir N projeto
    def botao_conferir_Projeto(self):
        N_projeto = self.campo_N_projeto.get().strip()

        # Verifica se foi informado apenas número
        if not N_projeto.isdigit():
            messagebox.showerror(
                title="ERRO",
                message="Erro no valor inserido!\n\nPor favor, escreva apenas números."
            )
            return

        self.numero_projeto = int(N_projeto)

        # Solicita o diretório
        self.selecionar_diretorio()

        # Verifica se o diretório foi selecionado corretamente
        if not self.diretorio:
            messagebox.showwarning(
                title="Diretório não selecionado",
                message="Por favor, selecione um diretório válido para continuar."
            )
            return

        # Tudo correto, pode iniciar
        self.botao_iniciar_processo()


    def atualizar_status(self, texto):
        self.label_status.configure(text=texto)
        # Desenha o texto antes de entrar nas chamadas bloqueantes do Selenium.
        self.app.update_idletasks()

    def botao_iniciar_processo(self):
        numero_projeto = self.numero_projeto
        diretorio = self.diretorio
        driver = None
        etapa = "login"
        self.botao_conferir_N_projeto.configure(state="disabled")
        try:
            self.atualizar_status("Realizando login...")
            driver = realizar_login(diretorio)
            etapa = "consulta dos contratos"
            self.atualizar_status("Buscando contratos...")
            resultados = buscar_contratos(driver, numero_projeto)

            for item in resultados:
                etapa = f"contrato {item['contrato']}"
                self.atualizar_status(f"Baixando anexos do contrato {item['contrato']}...")
                processar_contrato(driver, item, numero_projeto, diretorio)

            self.atualizar_status(
                "Downloads concluídos." if resultados else "Nenhum contrato encontrado."
            )
        except Exception:
            self.atualizar_status(f"Falha no processamento: {etapa}.")
            messagebox.showerror(title="Erro", message=f"Falha no processamento: {etapa}.")
            return
        finally:
            try:
                if driver is not None:
                    driver.quit()
            finally:
                self.botao_conferir_N_projeto.configure(state="normal")

        messagebox.showinfo(title="Sucesso", message="Todos os contratos foram processados com sucesso!")





    
