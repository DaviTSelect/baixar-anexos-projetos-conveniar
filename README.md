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
- Ao abrir, verifica atualizações automaticamente. Só abre o painel após confirmar a versão local. Uma versão nova exige download e execução do instalador; falhas mantêm o painel bloqueado.
- A espera do loader usa a invisibilidade de `imgLoad` com timeout; o seletor ainda precisa ser confirmado no Conveniar.
- Antes de processar os contratos, a busca rola até o fim da página e relê as linhas até permanecerem estáveis por dois segundos, com timeout de 30 segundos. O processamento começa pela primeira linha; a paginação ainda não está implementada.
- Os testes de regras exercitam a consulta real com navegador simulado. Consulte a [cobertura e as pendências de QA](docs/testes.md).
- As dependências de execução estão declaradas em `requirements.txt`.

## Fluxo pretendido

O painel gráfico permite inserir o número do projeto. A autenticação usa as credenciais fixas `USUARIO` e `SENHA` configuradas no `.env`, sem armazenamento em JSON ou campos de login no painel. A implementação visual está sendo realizada separadamente por outro integrante da equipe.

1. Realizar login.
2. Acessar a busca e selecionar `Contrato de Bolsa`.
3. Informar o projeto e limpar os filtros de data.
4. Consultar sem filtro de situação.
5. Percorrer todas as páginas e processar somente contratos `ATIVO` ou `ENCERRADO`.
6. Abrir cada contrato válido e acessar `Arquivos` para baixar os anexos.
7. Organizar os arquivos em `downloads/<numero_projeto>/<contrato>/`.

Esse fluxo descreve o objetivo do projeto. Atualmente, a busca limpa apenas a data inicial e não altera o filtro de situação; a seleção de contratos válidos ocorre na leitura das linhas retornadas.

## Downloads

A rotina baixa cada anexo em uma pasta isolada e move o arquivo concluído para a subpasta do projeto e do contrato, dentro da pasta escolhida no painel. Aguarda o loader desaparecer e o arquivo estabilizar sem extensões temporárias antes de seguir para o próximo anexo. As barras `/` do número do contrato são substituídas por `_`.

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
│   ├── launcher.py
│   ├── update.py
│   ├── main.py
│   ├── browser.py
│   ├── interface.py
│   └── config.py
├── tests/
│   ├── test_carregamento.py
│   ├── test_downloads.py
│   ├── test_envio_github.py
│   ├── test_interface_threads.py
│   ├── test_launcher.py
│   ├── test_regras.py
│   ├── test_update.py
│   └── test_update_ssl.py
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

O executável inclui os certificados do `certifi` para as conexões HTTPS de atualização, preservando também os certificados confiáveis do Windows. Se uma versão antiga apresentar `CERTIFICATE_VERIFY_FAILED`, atualize as dependências com `python -m pip install --upgrade certifi -r requirements-build.txt` e gere novamente o executável. Em redes com inspeção HTTPS, a autoridade certificadora da organização também precisa ser confiável no Windows; consulte a equipe de TI se a falha persistir.

## Consulta de atualizações

O inicializador consulta automaticamente a última release estável pública de `DaviTSelect/baixar-anexos-projetos-conveniar`, com timeout de 15 segundos na requisição. A versão local vem de `VERSAO_ATUAL`, em `src/update.py` (atualmente `1.1.2`); esse valor não comprova publicação.

- Versão local igual ou superior: abre o painel.
- Versão nova: baixa o primeiro arquivo terminado em `.exe` e tenta executá-lo como instalador no Windows. O aplicativo atual encerra; a instalação e a reabertura dependem do arquivo publicado.
- Falha de rede, certificado, release inválida ou ausência de instalador: oferece **Tentar novamente**, sem liberar o painel.
- Fechar fora do download encerra sem abrir o painel. Durante o download, o fechamento é bloqueado.

Não existe opção de continuar sem verificar. Os dois painéis usam fundo azul, textos claros e botões laranja; diálogos nativos seguem o tema do Windows.

O download da atualização usa timeout de 60 segundos na conexão e leitura, mostra progresso quando o tamanho é informado e salva na pasta temporária do sistema. Não há verificação de assinatura, hash ou comparação final com o tamanho anunciado. Veja o [guia técnico](docs/desenvolvimento.md#threads-e-consulta-de-releases).

Esta cópia contém apenas `criar_executavel.py` para empacotamento; não contém os antigos scripts de geração de launcher independente. Gerar o executável não cria um instalador. Consulte [versionamento e distribuição](docs/versionamento.md) antes de publicar uma release.

## Execução e testes

Na raiz que contém `src/` e `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
python src/main.py
```

Configure o `.env` e os caminhos do Chrome antes de executar. Para os testes locais, não é necessário configurar credenciais nem abrir o navegador:

```powershell
python -B -m pytest -p no:cacheprovider
```

A suíte inclui uma falha esperada para consultas simultâneas no inicializador. Veja a [matriz de testes e validação](docs/testes.md).

## Limitações que afetam o resultado

Não há paginação; a consulta limpa apenas a data inicial e não altera o filtro de situação. Uma falha interrompe os contratos restantes. Se a tabela de anexos não aparecer, ocorre timeout. Nomes iguais preservam o arquivo existente sem comparar conteúdo.

A mensagem **Downloads concluídos** indica o fim dos contratos retornados pela consulta atual, sem relatório de completude do projeto. Confira o resultado no Conveniar antes de considerá-lo completo.
