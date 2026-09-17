# Baixar Anexos de Contratos de Bolsistas por Projeto

Automação interna do setor de projetos para baixar os anexos dos contratos de bolsistas vinculados a um projeto no Conveniar.

| Campo | Valor |
| --- | --- |
| Prioridade | 2 |
| Status | Em desenvolvimento |

## Estado atual

O código contém rotinas de login, busca e download, mas o fluxo completo ainda não está operacional:

- A interface permite informar o projeto, selecionar a pasta e iniciar a automação. Um rótulo mostra o contrato cujos anexos estão sendo processados, além das etapas de login, consulta, conclusão ou falha.
- `aguardar_loader_desaparecer` lança `NotImplementedError`, interrompendo as rotinas que a chamam.
- Antes de processar os contratos, a busca rola até o fim da página e relê as linhas até permanecerem estáveis por dois segundos, com timeout de 30 segundos. O processamento começa pela primeira linha; a paginação ainda não está implementada.
- `tests/test_regras.py` importa `src.contratos`, módulo ausente no repositório.
- As dependências de execução estão declaradas em `requirements.txt`.

## Fluxo pretendido

O painel gráfico permitirá inserir o número do projeto. A autenticação usa as credenciais fixas `USUARIO` e `SENHA` configuradas no `.env`, sem armazenamento em JSON ou campos de login no painel. A implementação visual está sendo realizada separadamente por outro integrante da equipe.

1. Realizar login.
2. Acessar a busca e selecionar `Contrato de Bolsa`.
3. Informar o projeto e limpar os filtros de data.
4. Consultar sem filtro de situação.
5. Percorrer todas as páginas e processar somente contratos `ATIVO` ou `ENCERRADO`.
6. Abrir cada contrato válido e acessar `Arquivos` para baixar os anexos.
7. Organizar os arquivos em `downloads/<numero_projeto>/<contrato>/`.

Esse fluxo descreve o objetivo do projeto. Atualmente, a busca limpa apenas a data inicial e não altera o filtro de situação; a seleção de contratos válidos ocorre na leitura das linhas retornadas.

## Downloads

A rotina usa `downloads/` como diretório inicial do navegador e move cada arquivo para a subpasta do projeto e do contrato. As barras `/` do número do contrato são substituídas por `_`.

Exemplo: o contrato `1250/2026` do projeto `377` usa `downloads/377/1250_2026/`.

Se já existir um arquivo com o mesmo nome no destino, a rotina mantém o existente e exclui o novo download. Não há comparação de conteúdo nem geração de nomes alternativos.

## Configuração atual

`src/config.py` lê o arquivo `.env` da raiz do projeto:

| Variável | Uso |
| --- | --- |
| `URL` | Endereço acessado no login |
| `USUARIO` | Usuário de acesso |
| `SENHA` | Senha de acesso |
| `HEADLESS` | Ativa o modo sem janela do Chrome quando o valor, após normalização, é `true`; padrão: `true` |

O navegador está configurado para Windows e exige estes caminhos dentro de `%USERPROFILE%`:

- `Chrome\chromedriver.exe`
- `Chrome\GoogleChrome\App\Chrome-bin\chrome.exe`

A interface gráfica depende de um ambiente com suporte a Tkinter. `HEADLESS` controla somente o navegador.

Nunca versionar `.env` nem incluir credenciais nos logs ou na documentação.

## Estrutura

```text
baixar-anexos-projetos-conveniar/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── browser.py
│   ├── interface.py
│   └── config.py
├── tests/
│   ├── __init__.py
│   ├── test_envio_github.py
│   └── test_regras.py
├── docs/
│   ├── componentes-interface.md
│   ├── github-basico.md
│   └── desenvolvimento.md
├── ferramentas/
│   └── github/
│       ├── enviar.cmd
│       ├── enviar.py
│       ├── enviar.ps1
│       └── README.md
├── .github/
│   └── PULL_REQUEST_TEMPLATE.md
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
├── AGENTS.md
├── README.md
└── desenvolvimento.md
```

O arquivo `.env` contém a configuração local; `downloads/` armazena os arquivos baixados.

## Desenvolvimento

Consulte o [guia de desenvolvimento](docs/desenvolvimento.md) para responsabilidades dos módulos, limitações conhecidas e orientações de manutenção.

Para começar na equipe, leia o [guia básico de Git e GitHub](docs/github-basico.md) e os [exemplos de componentes de interface](docs/componentes-interface.md). Execute `python ferramentas/github/enviar.py` para informar a mensagem de commit e enviar a branch atual após revisar os arquivos e confirmar. No Windows, o atalho `enviar.cmd` chama esse mesmo script. Consulte as instruções em [ferramentas/github](ferramentas/github/README.md).

## Executável para Windows

Para gerar novamente o executável, execute na raiz do projeto:

```powershell
python -m pip install -r requirements-build.txt
python criar_executavel.py
```

O resultado é `dist/AnexosConveniar.exe`, com o ícone `icon/logo.ico` e os recursos da interface incluídos. Para usar, configure um arquivo `.env` ao lado do `.exe`, com as variáveis descritas acima. As credenciais não são incorporadas ao executável. Chrome e ChromeDriver continuam necessários nos caminhos indicados neste README; Python não é necessário na máquina que apenas executa o programa.

Consulte os detalhes de empacotamento no [guia de desenvolvimento](docs/desenvolvimento.md#geração-do-executável).
