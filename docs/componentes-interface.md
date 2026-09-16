# Componentes de interface: exemplos simples

O projeto usa **CustomTkinter** para a interface Python. O painel definitivo está com outro integrante da equipe; use os exemplos abaixo em um arquivo separado para estudar e combine alterações em `src/interface.py` com o responsável. O login continua no `.env`.

## Preparar e executar um exemplo

Com seu ambiente virtual ativo e Python com suporte a Tkinter, instale a biblioteca se necessário:

```powershell
python -m pip install customtkinter
```

Atualmente essa dependência ainda não está em `requirements.txt`. Salve o exemplo completo abaixo em `exemplo_interface.py`, na raiz, e execute:

```powershell
python exemplo_interface.py
```

Esse arquivo é somente para estudo: remova-o ao terminar e confira `git status` antes de enviar alterações. O exemplo não acessa o Conveniar nem baixa arquivos.

## O que cada componente faz

| Componente | Uso |
| --- | --- |
| `CTk` | Janela principal. |
| `CTkFrame` | Agrupa componentes em uma área. |
| `CTkLabel` | Exibe um texto, título ou estado. |
| `CTkEntry` | Recebe uma linha de texto, como o projeto. |
| `CTkButton` | Executa uma função quando clicado. |
| `CTkCheckBox` | Marca ou desmarca uma opção. |
| `CTkComboBox` | Permite escolher um item de uma lista. |
| `CTkTextbox` | Exibe ou recebe várias linhas. |
| `CTkProgressBar` | Indica andamento de uma operação. |

As opções de cada componente estão no [catálogo oficial do CustomTkinter](https://customtkinter.tomschimansky.com/documentation/widgets/).

## Exemplo completo: campo, botão e mensagem

```python
import customtkinter as ctk


class ExemploInterface:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("Estudo de componentes")
        self.app.geometry("460x300")

        painel = ctk.CTkFrame(self.app)
        painel.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(painel, text="Número do projeto").pack(pady=8)
        self.projeto = ctk.CTkEntry(painel, placeholder_text="Ex.: 377")
        self.projeto.pack(pady=8)

        self.botao = ctk.CTkButton(
            painel, text="Validar projeto", command=self.validar
        )
        self.botao.pack(pady=8)

        self.status = ctk.CTkLabel(painel, text="Informe um projeto.")
        self.status.pack(pady=8)

    def validar(self):
        numero = self.projeto.get().strip()
        if not numero.isascii() or not numero.isdigit():
            self.status.configure(text="Use apenas números, como 377.")
            return
        self.status.configure(text=f"Projeto {numero} pronto para teste.")

    def iniciar(self):
        self.app.mainloop()


if __name__ == "__main__":
    ExemploInterface().iniciar()
```

`self` dá acesso aos componentes da mesma instância da classe. Guardamos o campo em `self.projeto` para poder ler seu conteúdo dentro de `validar()`.

Em `command=self.validar`, passamos a função para o botão executar depois. Com `command=self.validar()`, a função seria executada durante a criação do botão.

`mainloop()` mantém a janela atendendo eventos, como cliques e digitação. Chame-o uma vez para a janela principal.

## Ler e alterar componentes

Os trechos abaixo usam os componentes da classe anterior. Coloque-os em um método da classe ou adapte os nomes:

```python
numero = self.projeto.get()                  # Lê o campo
self.projeto.delete(0, "end")                # Limpa o campo
self.projeto.insert(0, "377")                # Preenche o campo
self.status.configure(text="Consultando...")
self.botao.configure(state="disabled")      # Impede novos cliques
self.botao.configure(state="normal")        # Habilita novamente
```

## Organizar com pack ou grid

`pack()` é simples para empilhar componentes. `padx` e `pady` dão espaço ao redor; `fill` permite preencher a área e `expand=True` aproveita espaço extra.

`grid()` organiza por linha e coluna. Este trecho pode ser inserido em `__init__`, depois de criar `painel`:

```python
linha = ctk.CTkFrame(painel)
linha.pack(fill="x", padx=12, pady=8)
linha.grid_columnconfigure(1, weight=1)

ctk.CTkLabel(linha, text="Descrição").grid(row=0, column=0, padx=8)
ctk.CTkEntry(linha).grid(row=0, column=1, padx=8, sticky="ew")
```

Não misture `pack` e `grid` nos filhos do mesmo contêiner. Aqui `linha` usa `pack` dentro de `painel`, enquanto seus próprios filhos usam `grid` dentro de `linha`.

## Opções e progresso

Para experimentar, insira em `__init__`, depois de criar `painel`, e aumente a altura da janela:

```python
self.detalhes = ctk.CTkCheckBox(painel, text="Mostrar detalhes")
self.detalhes.pack(pady=4)

self.visualizacao = ctk.CTkComboBox(
    painel, values=["Resumo", "Detalhes"], state="readonly"
)
self.visualizacao.set("Resumo")
self.visualizacao.pack(pady=4)

self.progresso = ctk.CTkProgressBar(painel)
self.progresso.pack(pady=4)
self.progresso.set(0.5)  # Exemplo visual: metade concluída
```

Em um método, use `self.detalhes.get()` para obter `1` ou `0` e `self.visualizacao.get()` para ler a escolha. Essas opções são didáticas e não mudam as regras de consulta do projeto.

## Como conectar com a automação depois

A integração deve chamar `realizar_login()` sem argumentos e passar o projeto para `buscar_contratos(driver, numero_projeto)`. Não acrescente campos de usuário ou senha. O fluxo real ainda está bloqueado pelo loader e pelas demais limitações do [guia técnico](desenvolvimento.md).

Selenium e downloads podem demorar. Colocá-los diretamente na função do botão bloqueia o atendimento dos eventos da janela. Ao implementar essa integração, execute o trabalho demorado em uma thread e comunique os resultados por uma fila (`queue.Queue`). Na thread principal, consulte a fila periodicamente com `self.app.after(...)` e atualize os componentes ali. Não leia ou altere widgets na thread de trabalho. Essa separação segue as restrições do [modelo de execução do Tkinter](https://docs.python.org/3/library/tkinter.html#threading-model).

Desabilite o botão durante a operação, trate falhas, reabilite-o ao terminar e defina como encerrar o navegador. Não mostre “login realizado” ou “download concluído” apenas porque o botão foi clicado.
