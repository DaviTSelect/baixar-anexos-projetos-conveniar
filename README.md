# Baixar Anexos de Contratos de Bolsistas por Projeto

Automação interna do setor de projetos para baixar os anexos dos contratos de bolsistas vinculados a um projeto no Conveniar.

| Campo | Valor |
| --- | --- |
| Prioridade | 2 |
| Status | Em desenvolvimento |

## Estado atual

O código contém rotinas de login, busca e download, mas o fluxo completo ainda precisa de validação no Conveniar:

- A interface permite informar o projeto, selecionar a pasta e iniciar a automação. Um rótulo mostra o contrato cujos anexos estão sendo processados, além das etapas de login, consulta, conclusão ou falha.
- Login, consulta e downloads executam em uma thread separada, mantendo a janela responsiva. Ao fechar durante o processamento, o aplicativo aguarda o contrato atual e encerra o navegador.
- Ao abrir, oferece verificar atualizações ou continuar usando a versão atual. A consulta roda em segundo plano e permite abrir a página de download quando há versão mais recente.
- A espera do loader usa a invisibilidade de `imgLoad` com timeout; o seletor ainda precisa ser confirmado no Conveniar.
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

A rotina configura a pasta escolhida no painel como destino dos downloads e move cada arquivo para a subpasta do projeto e do contrato. As barras `/` do número do contrato são substituídas por `_`.

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

O resultado é `dist/Anexos - Contratos por Projeto.exe`, com o ícone `icon/logo.ico` e os recursos da interface incluídos. Para usar, configure um arquivo `.env` ao lado do `.exe`, com as variáveis descritas acima. As credenciais não são incorporadas ao executável. Chrome e ChromeDriver continuam necessários nos caminhos indicados neste README; Python não é necessário na máquina que apenas executa o programa.

Consulte os detalhes de empacotamento no [guia de desenvolvimento](docs/desenvolvimento.md#geração-do-executável).

## Consulta de atualizações

Os dois painéis usam fundo azul `#203447`, textos brancos `#efede5` e botões laranja `#e94c1f`. Diálogos nativos de aviso e seleção de pasta seguem a aparência do Windows.

Para gerar novamente o launcher independente de atualizações, execute `python gerar_launcher.py`. O script cria `launcher.py` na raiz usando a implementação mantida em `src/launcher.py`; depois, execute `python launcher.py` para abrir a consulta de atualizações.

Para gerar o launcher como executável independente no Windows, execute `python criar_executavel_launcher.py`. O resultado será `dist/Launcher - Anexos - Contratos por Projeto.exe`; ele pode ser distribuído sem Python e consulta as atualizações antes de abrir o aplicativo principal. Feche o executável antes de recompilar.

A tela inicial oferece **Verificar atualização** e **Continuar usando a versão atual**. A consulta busca a última release estável pública de `DaviTSelect/baixar-anexos-projetos-conveniar`, com timeout de 10 segundos na requisição. É possível continuar mesmo durante a consulta; falta de rede, limite da API ou ausência de release não impedem o uso. Quando há atualização, **Abrir página para download** abre a release no navegador, para download manual, sem instalar ou substituir arquivos. Fechar a tela inicial encerra o aplicativo sem abrir o painel.

A versão local está em `VERSAO_ATUAL`, no arquivo `src/update.py`, atualmente `1.0.0`; isso não comprova a existência de uma release publicada. Antes de distribuir, defina o número aprovado, gere o executável e publique uma release com a tag correspondente (`vMAJOR.MINOR.PATCH`). Commits enviados ao GitHub não geram avisos de atualização por si só. Execute `python src/main.py` para usar pelo código-fonte; executáveis existentes precisam ser recompilados para incorporar a correção.
