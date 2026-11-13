from queue import Queue, Empty
from threading import Thread, Event
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

from datetime import datetime
from pathlib import Path
import sys
import openpyxl
from browser import realizar_login
from browser import buscar_contratos
from browser import processar_contrato
from config import BASE_DIR


def gerar_relatorio(numero_projeto, resultados):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Relatorio"
    ws.append(["Projeto", "Contrato", "Situacao", "Resultado", "Anexos Baixados", "Detalhe"])
    for r in resultados:
        ws.append([
            r["projeto"],
            r["contrato"],
            r["situacao"],
            r["resultado"],
            r["baixados"],
            r["detalhe"],
        ])
    for col in ws.columns:
        largura = max(len(str(cell.value or "")) for cell in col)
        ws.column_dimensions[col[0].column_letter].width = min(largura + 2, 60)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    caminho = BASE_DIR / f"relatorio_{numero_projeto}_{timestamp}.xlsx"
    wb.save(str(caminho))
    print(f"Relatório gerado: {caminho}")
    return caminho





class InterfaceAutomacao:

    


    def __init__(self):
        self.app = CTk()

        set_appearance_mode("Dark")
        self.app.configure(fg_color="#203447")

        self.app.title("Anexos - Contratos por Projeto")
        self.app.geometry("400x300")
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
        self.eventos = Queue()
        self.cancelar = Event()
        self.executando = False
        self.fechando = False
        self.worker = None
        self.app.protocol("WM_DELETE_WINDOW", self.fechar)
        self.app.after(100, self.consumir_eventos)

    def iniciar(self):
        self.app.mainloop()

    def definir_icone(self, caminho_icone):
        self.icon = caminho_icone


#função 
    def criar_componentes(self):
        #coloque os componentes aqui
        #criando frame fundo do projeto 1
        self.Frame_fundoProjeto1 = CTkFrame(self.app, width=250, fg_color="#203447")
        self.Frame_fundoProjeto1.grid(row=0, column=1, sticky="ns")
        self.Frame_fundoProjeto1.pack(pady=(20, 10), padx=(2, 2))

        #criando texto do numero do projeto
        self.label_Nprojeto = CTkLabel(self.Frame_fundoProjeto1,
                                      text="Anexos - Contratos por Projeto",
                                      text_color="#efede5",
                                      font=CTkFont(size=20, weight="bold"))
        self.label_Nprojeto.pack(pady=(10, 10), padx=(20, 20))

        #criando canpo para digitar o numero do projeto
        self.campo_N_projeto = CTkEntry(
            self.app, placeholder_text="Digite o numero do projeto", width=300,
            fg_color="#203447", text_color="#efede5",
            placeholder_text_color="#efede5", border_color="#efede5",
        )

        self.campo_N_projeto.pack(pady=(50,10))

        #criando botao para conferir o numero do projeto
        self.botao_conferir_N_projeto = CTkButton(self.app,
                                                  text="Buscar",
                                                  fg_color="#e94c1f", hover_color="#e94c1f",
                                                  text_color="#efede5", text_color_disabled="#efede5",
                                                  command=self.botao_conferir_Projeto)
        self.botao_conferir_N_projeto.pack(pady=(10,10))

        self.label_status = CTkLabel(self.app, text="Aguardando início.", wraplength=550,
                                     text_color="#efede5")
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
        if self.executando or self.fechando:
            return
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

    def botao_iniciar_processo(self):
        if self.executando or self.fechando:
            return
        self.executando = True
        self.cancelar.clear()
        self.botao_conferir_N_projeto.configure(state="disabled")
        self.campo_N_projeto.configure(state="disabled")
        self.worker = Thread(
            target=self.executar_automacao,
            args=(self.numero_projeto, self.diretorio),
            daemon=False,
        )
        self.worker.start()

    def executar_automacao(self, numero_projeto, diretorio):
        # O navegador pertence exclusivamente a esta thread. Só a fila chega à GUI.
        driver = None
        etapa = "login"
        erro = None
        texto = "Processamento interrompido."
        resultados_contratos = []
        try:
            if self.cancelar.is_set():
                return
            self.eventos.put(("status", "Realizando login..."))
            driver = realizar_login()
            if self.cancelar.is_set():
                return
            etapa = "configuração da pasta de downloads"
            diretorio.mkdir(parents=True, exist_ok=True)
            driver.execute_cdp_cmd("Browser.setDownloadBehavior", {
                "behavior": "allow", "downloadPath": str(diretorio.resolve()),
            })
            etapa = "consulta dos contratos"
            self.eventos.put(("status", "Buscando contratos..."))
            resultados = buscar_contratos(driver, numero_projeto)
            for item in resultados:
                if self.cancelar.is_set():
                    return
                etapa = f"contrato {item['contrato']}"
                self.eventos.put(("status", f"Baixando anexos do contrato {item['contrato']}..."))
                try:
                    r = processar_contrato(driver, item, numero_projeto, diretorio)
                    if r.get("sem_tabela"):
                        resultado_texto = "Sem anexos"
                        detalhe = "Tabela de arquivos não encontrada"
                    elif r["baixados"] == 0:
                        resultado_texto = "Sem anexos"
                        detalhe = ""
                    else:
                        resultado_texto = "Sucesso"
                        detalhe = ""
                    resultados_contratos.append({
                        "projeto": numero_projeto,
                        "contrato": item["contrato"],
                        "situacao": item["status"],
                        "resultado": resultado_texto,
                        "baixados": r["baixados"],
                        "detalhe": detalhe,
                    })
                except Exception as e_contrato:
                    resultados_contratos.append({
                        "projeto": numero_projeto,
                        "contrato": item["contrato"],
                        "situacao": item["status"],
                        "resultado": "Erro",
                        "baixados": 0,
                        "detalhe": str(e_contrato),
                    })
            if not resultados:
                texto = "Nenhum contrato encontrado."
            else:
                erros = sum(1 for r in resultados_contratos if r["resultado"] == "Erro")
                texto = "Downloads concluídos."
                if erros:
                    texto += f" ({erros} contrato(s) com erro)"
                try:
                    etapa = "geração do relatório"
                    caminho = gerar_relatorio(numero_projeto, resultados_contratos)
                    texto += f"\nRelatório: {caminho.name}"
                except Exception:
                    texto += "\nFalha ao gerar relatório."
        except Exception:
            erro = f"Falha no processamento: {etapa}."
        finally:
            if driver is not None:
                try:
                    driver.quit()
                except Exception:
                    erro = erro or "Falha ao encerrar o navegador."
            self.eventos.put(("fim", (texto, erro)))

    def consumir_eventos(self):
        try:
            while True:
                tipo, dados = self.eventos.get_nowait()
                if tipo == "status" and not self.fechando:
                    self.atualizar_status(dados)
                elif tipo == "fim":
                    self.executando = False
                    if not self.fechando:
                        texto, erro = dados
                        self.botao_conferir_N_projeto.configure(state="normal")
                        self.campo_N_projeto.configure(state="normal")
                        self.atualizar_status(erro or texto)
                        if erro:
                            messagebox.showerror(title="Erro", message=erro, parent=self.app)
                        else:
                            messagebox.showinfo(title="Conclusão", message=texto, parent=self.app)
        except Empty:
            pass
        if self.fechando and (self.worker is None or not self.worker.is_alive()):
            self.app.destroy()
            return
        self.app.after(100, self.consumir_eventos)

    def fechar(self):
        self.fechando = True
        self.cancelar.set()
        self.botao_conferir_N_projeto.configure(state="disabled")
        self.atualizar_status("Encerrando: aguardando a operação atual e fechando o navegador...")
