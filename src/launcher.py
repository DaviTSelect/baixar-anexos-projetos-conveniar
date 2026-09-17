from queue import Empty, Queue
from threading import Thread

import os
import sys
import tkinter as tk

from tkinter import messagebox


if __package__:
    from .update import (
        STATUS_ATUALIZADO,
        STATUS_DISPONIVEL,
        STATUS_ERRO,
        verificar_atualizacoes,
        baixar_atualizacao,
    )
else:
    from update import (
        STATUS_ATUALIZADO,
        STATUS_DISPONIVEL,
        STATUS_ERRO,
        verificar_atualizacoes,
        baixar_atualizacao,
    )


class Inicializador:

    def __init__(self):

        self.app = tk.Tk()

        self.app.title("Atualização")
        self.app.geometry("420x220")
        self.app.resizable(False, False)
        self.app.configure(bg="#203447")

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        self.status = tk.Label(
            self.app,
            text="Verificando atualizações...",
            wraplength=380,
            bg="#203447",
            fg="#efede5",
            font=("Arial", 11),
        )

        self.status.pack(
            padx=20,
            pady=(30, 15),
        )

        # -------------------------------------------------
        # PROGRESSO
        # -------------------------------------------------

        self.progresso = tk.Label(
            self.app,
            text="",
            bg="#203447",
            fg="#efede5",
        )

        self.progresso.pack(
            pady=5
        )

        # -------------------------------------------------
        # BOTÃO TENTAR NOVAMENTE
        # -------------------------------------------------

        estilo = {
            "bg": "#e94c1f",
            "fg": "#efede5",
            "activebackground": "#e94c1f",
            "activeforeground": "#efede5",
            "relief": "flat",
            "padx": 15,
            "pady": 6,
        }

        self.botao_tentar = tk.Button(
            self.app,
            text="Tentar novamente",
            command=self.verificar,
            **estilo,
        )

        # Começa escondido.
        self.botao_visivel = False

        # -------------------------------------------------
        # CONTROLE
        # -------------------------------------------------

        self.eventos = Queue()

        self.fechando = False
        self.baixando = False
        self.abrindo_programa = False

        # IMPORTANTE:
        # Somente fica True quando confirmamos que
        # a versão atual pode ser executada.
        self.pode_iniciar_programa = False

        self.url_download = None
        self.arquivo_download = None

        self.app.protocol(
            "WM_DELETE_WINDOW",
            self.fechar,
        )

        self.agendamento = self.app.after(
            100,
            self.consumir_eventos,
        )

    # =====================================================
    # INICIALIZAÇÃO
    # =====================================================

    def iniciar(self):

        self.app.after(
            300,
            self.verificar,
        )

        self.app.mainloop()

        # O main.py depende deste retorno.
        #
        # True:
        #   versão atualizada -> abre InterfaceAutomacao.
        #
        # False:
        #   usuário fechou ou instalador foi iniciado.
        return self.pode_iniciar_programa

    # =====================================================
    # BOTÃO
    # =====================================================

    def mostrar_botao_tentar(self):

        if self.botao_visivel:
            return

        self.botao_tentar.configure(
            state="normal"
        )

        self.botao_tentar.pack(
            pady=10
        )

        self.botao_visivel = True

    def esconder_botao_tentar(self):

        if not self.botao_visivel:
            return

        self.botao_tentar.pack_forget()

        self.botao_visivel = False

    # =====================================================
    # VERIFICAÇÃO
    # =====================================================

    def verificar(self):

        if (
            self.fechando
            or self.baixando
            or self.abrindo_programa
        ):
            return

        self.esconder_botao_tentar()

        self.botao_tentar.configure(
            state="disabled"
        )

        self.url_download = None

        self.status.configure(
            text="Verificando a versão mais recente..."
        )

        self.progresso.configure(
            text=""
        )

        Thread(
            target=self.executar_verificacao,
            daemon=True,
        ).start()

    def executar_verificacao(self):

        try:

            resultado = verificar_atualizacoes()

        except Exception as erro:

            resultado = (
                (
                    "Erro ao verificar atualização:\n"
                    f"{erro}"
                ),
                STATUS_ERRO,
                None,
            )

        self.eventos.put(
            (
                "verificacao",
                resultado,
            )
        )

    # =====================================================
    # DOWNLOAD
    # =====================================================

    def iniciar_download(self):

        if self.baixando:
            return

        if not self.url_download:
            return

        self.baixando = True

        self.esconder_botao_tentar()

        self.status.configure(
            text="Baixando a nova versão..."
        )

        self.progresso.configure(
            text="Iniciando download..."
        )

        Thread(
            target=self.executar_download,
            daemon=True,
        ).start()

    def executar_download(self):

        try:

            def progresso(
                percentual,
                baixados,
                total,
            ):

                self.eventos.put(
                    (
                        "progresso",
                        percentual,
                        baixados,
                        total,
                    )
                )

            arquivo = baixar_atualizacao(
                self.url_download,
                progresso=progresso,
            )

            self.eventos.put(
                (
                    "download_ok",
                    arquivo,
                )
            )

        except Exception as erro:

            self.eventos.put(
                (
                    "download_erro",
                    str(erro),
                )
            )

    # =====================================================
    # EVENTOS DA INTERFACE
    # =====================================================

    def consumir_eventos(self):

        if self.fechando:
            return

        try:

            while True:

                evento = self.eventos.get_nowait()

                tipo = evento[0]

                # =========================================
                # RESULTADO DA VERIFICAÇÃO
                # =========================================

                if tipo == "verificacao":

                    (
                        texto,
                        status,
                        url,
                    ) = evento[1]

                    # -------------------------------------
                    # VERSÃO ATUALIZADA
                    # -------------------------------------

                    if status == STATUS_ATUALIZADO:

                        self.status.configure(
                            text=texto
                        )

                        self.progresso.configure(
                            text="Abrindo programa..."
                        )

                        self.app.after(
                            500,
                            self.abrir_programa,
                        )

                    # -------------------------------------
                    # NOVA VERSÃO
                    # -------------------------------------

                    elif status == STATUS_DISPONIVEL:

                        self.url_download = url

                        self.status.configure(
                            text=(
                                texto
                                + "\n\n"
                                "A atualização é obrigatória."
                            )
                        )

                        self.iniciar_download()

                    # -------------------------------------
                    # ERRO
                    # -------------------------------------

                    elif status == STATUS_ERRO:

                        self.status.configure(
                            text=texto
                        )

                        self.progresso.configure(
                            text=""
                        )

                        self.mostrar_botao_tentar()

                    # -------------------------------------
                    # STATUS DESCONHECIDO
                    # -------------------------------------

                    else:

                        self.status.configure(
                            text=(
                                "A verificação retornou "
                                "um estado desconhecido."
                            )
                        )

                        self.progresso.configure(
                            text=""
                        )

                        self.mostrar_botao_tentar()

                # =========================================
                # PROGRESSO
                # =========================================

                elif tipo == "progresso":

                    percentual = evento[1]
                    baixados = evento[2]
                    total = evento[3]

                    baixados_mb = (
                        baixados / 1024 / 1024
                    )

                    if percentual >= 0 and total > 0:

                        total_mb = (
                            total / 1024 / 1024
                        )

                        self.progresso.configure(
                            text=(
                                f"Baixando... {percentual}% "
                                f"({baixados_mb:.1f} MB"
                                f" / {total_mb:.1f} MB)"
                            )
                        )

                    else:

                        self.progresso.configure(
                            text=(
                                "Baixando... "
                                f"{baixados_mb:.1f} MB"
                            )
                        )

                # =========================================
                # DOWNLOAD CONCLUÍDO
                # =========================================

                elif tipo == "download_ok":

                    self.baixando = False

                    self.arquivo_download = (
                        evento[1]
                    )

                    self.status.configure(
                        text=(
                            "Download concluído.\n"
                            "Abrindo instalador..."
                        )
                    )

                    self.progresso.configure(
                        text=""
                    )

                    self.app.after(
                        500,
                        self.instalar,
                    )

                # =========================================
                # ERRO NO DOWNLOAD
                # =========================================

                elif tipo == "download_erro":

                    self.baixando = False

                    erro = evento[1]

                    self.status.configure(
                        text=(
                            "Não foi possível baixar "
                            "a atualização."
                        )
                    )

                    self.progresso.configure(
                        text=erro
                    )

                    self.mostrar_botao_tentar()

                    messagebox.showerror(
                        "Atualização obrigatória",
                        (
                            "A versão atual não pode ser "
                            "utilizada porque existe uma "
                            "versão mais recente.\n\n"
                            f"Erro:\n{erro}"
                        ),
                        parent=self.app,
                    )

        except Empty:
            pass

        if not self.fechando:

            self.agendamento = self.app.after(
                100,
                self.consumir_eventos,
            )

    # =====================================================
    # ABRIR PROGRAMA ATUAL
    # =====================================================

    def abrir_programa(self):
        """
        Libera o main.py para abrir a aplicação.

        NÃO chama main() novamente.
        Isso evita loop infinito.
        """

        if self.abrindo_programa:
            return

        self.abrindo_programa = True

        # O main.py receberá True.
        self.pode_iniciar_programa = True

        self.fechando = True

        try:

            self.app.after_cancel(
                self.agendamento
            )

        except Exception:
            pass

        self.app.destroy()

    # =====================================================
    # INSTALAÇÃO
    # =====================================================

    def instalar(self):
        """
        Executa o instalador da nova versão.

        O programa atual termina depois de iniciar
        o instalador.

        O instalador deve abrir o executável atualizado
        depois que a instalação terminar.
        """

        if not self.arquivo_download:
            return

        try:

            if sys.platform != "win32":

                raise OSError(
                    "O instalador baixado é um .exe "
                    "e este aplicativo está fora do Windows."
                )

            # Executa o instalador.
            os.startfile(
                self.arquivo_download
            )

            # IMPORTANTE:
            # Continua False para impedir que o main.py
            # abra a versão antiga.
            self.pode_iniciar_programa = False

            self.fechando = True

            try:

                self.app.after_cancel(
                    self.agendamento
                )

            except Exception:
                pass

            self.app.destroy()

        except Exception as erro:

            self.fechando = False

            self.status.configure(
                text=(
                    "Não foi possível iniciar "
                    "o instalador."
                )
            )

            self.progresso.configure(
                text=str(erro)
            )

            self.mostrar_botao_tentar()

            messagebox.showerror(
                "Erro na atualização",
                str(erro),
                parent=self.app,
            )

    # =====================================================
    # FECHAR
    # =====================================================

    def fechar(self):

        # Não permite fechar durante download
        # de uma atualização obrigatória.
        if self.baixando:

            messagebox.showwarning(
                "Atualização obrigatória",
                (
                    "A atualização está sendo baixada.\n\n"
                    "É necessário aguardar a conclusão."
                ),
                parent=self.app,
            )

            return

        # Fechamento manual nunca libera o programa.
        self.pode_iniciar_programa = False
        self.fechando = True

        try:

            self.app.after_cancel(
                self.agendamento
            )

        except Exception:
            pass

        self.app.destroy()