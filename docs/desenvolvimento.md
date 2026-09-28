# Desenvolvimento

Este guia descreve o código existente e separa as regras pretendidas das funcionalidades ainda pendentes. Consulte o [README](../README.md) para a configuração e a estrutura do projeto.

Para apoio ao estagiário, consulte o [guia básico de Git e GitHub](github-basico.md), o [atalho de commit e envio da branch atual](../ferramentas/github/README.md) e os [exemplos de componentes de interface](componentes-interface.md). Os exemplos são material de estudo; o painel definitivo continua sob responsabilidade do integrante designado.

## Responsabilidades dos módulos

| Arquivo | Responsabilidade atual |
| --- | --- |
| `src/main.py` | Abre o inicializador e só instancia `InterfaceAutomacao` quando a versão atual é liberada. |
| `src/launcher.py` | Coordena consulta, download e execução obrigatórios da atualização antes do painel. |
| `src/update.py` | Consulta a release pública, compara versões e baixa o primeiro `.exe`. |
| `src/interface.py` | Cria a janela CustomTkinter, recebe o projeto e a pasta, inicia a automação e mostra o contrato em processamento. |
| `src/browser.py` | Contém as rotinas de login, consulta e download, além da espera do loader por invisibilidade de `imgLoad`. |
| `src/config.py` | Lê as variáveis de ambiente e define os caminhos da raiz e dos downloads. |
| `tests/test_regras.py` | Exercita a filtragem de `buscar_contratos()` com navegador simulado. |

## Integração do painel e autenticação

O inicializador (`src/launcher.py`, Tkinter) e o painel principal (`src/interface.py`, CustomTkinter) usam fundo `#203447`, texto `#efede5` e botões `#e94c1f`, com cores explícitas nos widgets. Os diálogos nativos mantêm o tema do sistema operacional.

O painel possui entrada para o número do projeto, seleção de pasta e botão de execução. O rótulo de status mostra login, consulta e `Baixando anexos do contrato <número>...` antes de processar cada contrato. Ao terminar, indica conclusão, ausência de contratos ou a etapa que falhou.

Login, consulta, download e encerramento do navegador executam em uma única thread de trabalho. Ela publica mensagens em `Queue`; `after(100, ...)` consome a fila na thread principal, responsável por todos os widgets e diálogos. O botão e o campo do projeto ficam desabilitados durante o processamento, impedindo execuções simultâneas. O rótulo identifica o contrato, sem medir o progresso de cada arquivo.

Ao fechar a janela, um `Event` solicita interrupção entre etapas e contratos. A janela continua atendendo eventos enquanto aguarda a operação em curso e `driver.quit()`; não há interrupção forçada de um download nem `join()` bloqueante na GUI. Uma chamada do navegador que não retorne pode atrasar esse encerramento. Falhas de processamento ou de fechamento são comunicadas sem expor a exceção bruta.

`realizar_login()` mantém as credenciais no `.env` e aceita também o parâmetro opcional de diretório para compatibilidade. O painel chama sem argumentos e, após o login, configura a pasta selecionada via `Browser.setDownloadBehavior`. O destino inicial padrão do login é `downloads/`. A configuração do destino via CDP precisa de validação com o Chrome utilizado pela equipe. O módulo do navegador não abre janelas Tk; arquivos de Chrome/ChromeDriver ausentes geram exceções. Se o login falhar depois de criar o navegador, ele tenta encerrá-lo antes de propagar a falha.

O painel deve chamar `realizar_login()` sem argumentos. A rotina usa `USUARIO` e `SENHA` de `src/config.py`, que carrega o `.env` da raiz. Não há persistência de credenciais em JSON, campos de login ou opção de logout local no painel. Os sinais de login e o seletor do loader ainda precisam de confirmação no sistema.

## Consulta e situação dos contratos

`buscar_contratos(driver, numero_projeto)` contém esta sequência:

1. Selecionar `Contrato de Bolsa`.
2. Informar o número do projeto e selecionar uma opção correspondente.
3. Limpar o campo de data inicial.
4. Acionar a consulta, rolar até o fim e reler as linhas da página atual até estabilizarem por dois segundos (timeout de 30 segundos), antes de começar pela primeira linha.
5. Ignorar linhas com menos de 11 colunas, de outro projeto ou sem link de contrato.
6. Retornar somente contratos cuja situação, após remoção de espaços nas extremidades e conversão para minúsculas, seja `ativo` ou `encerrado`.

A rotina não altera o filtro de situação. O requisito é consultar sem esse filtro e selecionar os contratos válidos nas linhas retornadas; não são previstas duas consultas separadas por situação.

`carregar_linhas_contratos` verifica `document.readyState`, a invisibilidade do loader existente `imgLoad` e a chegada ao fim da página. Relocaliza as linhas a cada verificação; mudanças na altura, nos elementos ou no texto reiniciam os dois segundos de estabilidade. Se a página crescer, volta a rolar até o novo final. O timeout interrompe a consulta sem processar uma lista parcial. Esses sinais não comprovam ausência de futuras requisições assíncronas; o comportamento precisa ser validado no Conveniar, inclusive o seletor do loader. A espera ocorre antes do laço de contratos da página atual.

Os testes isolados dessa espera usam navegador e relógio simulados, sem acessar credenciais: `python -B -m unittest discover -s tests -p test_carregamento.py`. Cobrem linhas tardias, substituição de elementos, tabela vazia, loader ativo, documento incompleto, posição de rolagem e crescimento contínuo com timeout.

Cada resultado contém `contrato`, `projeto`, `status` e `link`. O link é um elemento do Selenium, não uma URL armazenada como texto.

## Loader e paginação

`aguardar_loader_desaparecer(driver, timeout=30)` usa `WebDriverWait`, verifica o documento pronto e exige que os elementos `imgLoad` permaneçam invisíveis ou ausentes por um segundo contínuo. Se o loader aparecer nesse intervalo, a contagem reinicia. O seletor e seu comportamento ainda precisam de validação real no Conveniar; carregamentos que comecem após esse intervalo não são previstos pela espera.

O requisito é aguardar uma condição real da página com timeout após operações que provoquem carregamento. No processamento dos anexos, a abertura da janela e a espera do loader usam condições verificadas; `time.sleep()` é usado somente como intervalo de consulta do arquivo em disco.

A paginação ainda não foi implementada. As chamadas para rolar a página não constituem navegação entre páginas de resultados.

Quando implementada, a paginação deverá:

- Percorrer todas as páginas, inclusive as que não tenham contratos válidos.
- Evitar processar uma página duas vezes ou ignorar a última.
- Preservar a navegação ao retornar dos detalhes de um contrato.
- Evitar laços infinitos.

## Processamento e downloads

A sequência presente em `processar_contrato(driver, item, projeto, diretorio_destino)` é:

1. Criar `<diretorio_destino>/<projeto>/<contrato>/`, substituindo `/` por `_` no contrato.
2. Guardar as janelas existentes, clicar no link e aguardar uma nova janela por até 30 segundos.
3. Aguardar o loader desaparecer, abrir a aba `Arquivos` e localizar a tabela de anexos.
4. Contar os botões `Baixar arquivo` e relocalizá-los a cada download, evitando referências antigas após atualizações da tabela. A ordem dos anexos deve permanecer a mesma.
5. Configurar via CDP uma pasta exclusiva `.anexo-*` dentro da pasta do contrato para cada clique e aguardar o loader e o arquivo. Arquivos da pasta geral não são candidatos.
6. Mover o arquivo concluído para a pasta do contrato, se o nome ainda não existir, e remover a pasta temporária vazia antes do próximo anexo.
7. Restaurar a pasta de downloads, fechar a janela do contrato e retornar à anterior, inclusive em falhas. Arquivos parciais ficam preservados na pasta `.anexo-*` para inspeção.

A espera pelo arquivo tem timeout de 120 segundos, com consultas a cada 250 ms. Exige um único arquivo, sem parciais, com tamanho e data de modificação estáveis por um segundo e disponível para leitura. Mais de um arquivo completo causa erro de ambiguidade. O timeout interrompe o contrato e a mensagem identifica a etapa e o índice do anexo. A configuração do Chrome via CDP e o caso real do projeto 328 ainda precisam ser validados no Conveniar.

Os testes de regressão em `tests/test_downloads.py` simulam vários anexos, colisão de nomes, arquivos alheios na pasta geral, download parcial, crescimento do arquivo, timeout, loader tardio e restauração após falhas. Execute `python -B -m pytest tests/test_downloads.py tests/test_carregamento.py tests/test_interface_threads.py -p no:cacheprovider`.

Se o nome já existir no destino, o arquivo existente é mantido e o novo download é excluído. Não há comparação de conteúdo nem renomeação com sufixos. Arquivos de mesmo nome podem ter conteúdos diferentes; essa limitação deve ser considerada ao avaliar os resultados.

Se a tabela existir, mas não tiver botões de download, o laço de downloads fica vazio. Se a tabela não aparecer, a espera pode falhar por timeout. Portanto, o requisito de continuar após qualquer contrato sem anexos ainda não está plenamente atendido.

## Limitações conhecidas

Além do loader e da paginação:

- A busca limpa apenas a data inicial, sem limpar todos os filtros de data.
- O navegador depende dos caminhos fixos para Windows descritos no README.
- Uma exceção interrompe o processamento dos demais contratos. A thread tenta encerrar toda a sessão do navegador no `finally`.

O login ainda não verifica um sinal específico de autenticação após clicar em entrar. A mensagem final não contém contagem ou relatório de anexos pendentes. Uma indisponibilidade do GitHub bloqueia o painel, mesmo se o Conveniar estiver acessível.

Esses pontos são limitações registradas, não correções implementadas.

## Testes existentes

A suíte e a matriz de cobertura estão em [Testes e validação de QA](testes.md). Execute na raiz:

```powershell
python -B -m pytest -p no:cacheprovider
```

`test_regras.py` carrega `browser.py` com configuração fictícia e exercita `buscar_contratos()`: situações válidas, espaços nas extremidades, projeto correto, link, linhas incompletas, ordem e resultado vazio. Não depende de um módulo `src.contratos`.

Os testes de atualização usam o retorno atual de três valores: mensagem, status textual e URL. Os testes do inicializador simulam janelas, rede e execução do instalador. QA-01 permanece como `xfail(strict=True)`: a consulta não impede chamadas simultâneas. Uma correção futura fará esse teste sinalizar XPASS até retirar a marcação.

Os testes de envio usam repositórios e remotos locais temporários, sem publicar no GitHub. Requerem Git; os cenários PowerShell são ignorados se ele estiver ausente.

## Orientações de manutenção

Seguir o fluxo: entender o problema, implementar, validar, tratar erros relevantes, documentar e refatorar quando necessário.

Antes de alterar uma função, ler sua implementação, verificar onde é usada e analisar os testes relacionados. Preferir responsabilidades claras e evitar abstrações sem necessidade real. Docstrings devem explicar entradas, saídas e comportamento; comentários devem esclarecer decisões.

Essas orientações gerais não ampliam a autorização de uma tarefa. Em revisões restritas a Markdown, registrar problemas sem modificar código ou configuração.

### Logs e investigação de erros

O código atual usa `print()`; não há um sistema de logs estruturados com níveis `[INFO]`, `[WARNING]` e `[ERROR]`.

Registrar informações que ajudem a localizar a falha, sem senhas ou credenciais:

```text
Projeto:
Página:
Contrato:
Etapa:
Comportamento esperado:
Comportamento obtido:
Como reproduzir:
Mensagem apresentada:
```

Priorizar falhas de login, loader, navegação, download e acesso ao diretório. Evitar esconder exceções. Quando uma correção de código for autorizada, criar um teste de regressão se a falha puder ser representada por um teste útil.

### Git e revisão

Cada alteração deve ter um objetivo claro. Usar branches conforme necessário, como `feature/<tema>`, `fix/<problema>` ou `docs/<tema>`.

Os commits devem descrever a mudança com precisão, usando prefixos como `feat:`, `fix:`, `test:`, `docs:`, `refactor:` ou `chore:`.

Antes de abrir um pull request:

- Revisar o diff e confirmar que o escopo autorizado foi respeitado.
- Executar as validações pertinentes e registrar limitações ou bloqueios.
- Verificar se nenhuma credencial ou arquivo temporário foi incluído.
- Atualizar a documentação afetada.

Usar o [modelo de pull request](../.github/PULL_REQUEST_TEMPLATE.md) para explicar o que mudou, por quê, como foi validado e quais limitações permanecem. Em alterações exclusivamente documentais, a validação pode consistir na revisão dos links e na comparação das afirmações com o código, sem executar a automação.

## Geração do executável

O script [criar_executavel.py](../criar_executavel.py) usa PyInstaller no Windows para gerar `dist/Anexos - Contratos por Projeto.exe` em arquivo único, sem console. Instale as dependências de [requirements-build.txt](../requirements-build.txt) antes de executar o script. Ele usa caminhos relativos à sua própria localização, podendo ser chamado de outro diretório.

O ícone é incorporado tanto ao arquivo executável quanto como recurso da janela. Os dados do CustomTkinter também são incluídos. A localização dos recursos usa `sys._MEIPASS` quando empacotado; a configuração externa usa a pasta de `sys.executable`, conforme a [documentação do PyInstaller](https://pyinstaller.org/en/stable/runtime-information.html).

O `.env` deve ficar ao lado do executável; em execução pelo código-fonte, continua na raiz do repositório. O script não copia nem incorpora credenciais, Chrome ou ChromeDriver. Não é necessário distribuir a pasta `icon` separadamente.

Cada compilação atualiza o executável de mesmo nome em `dist/`; feche o programa antes de recompilar. Os arquivos intermediários e o spec gerado ficam em `build/`, preservando o `main.spec` preexistente. `build/` e `dist/` são ignorados pelo Git. Use o script como procedimento de compilação; o `main.spec` antigo aponta para outro nome de ícone.

O empacotamento não valida login, seletores nem downloads no Conveniar. As descrições anteriores da interface e automação ainda precisam ser reconciliadas com as alterações locais feitas pela equipe.

O empacotamento inclui explicitamente os módulos `selenium.webdriver.chrome.webdriver` e `selenium.webdriver.chrome.options`, carregados dinamicamente pelo Selenium, além dos arquivos de dados da biblioteca. Sem esses módulos, o código-fonte pode funcionar, mas o executável falha antes de iniciar o Chrome com `ModuleNotFoundError`. Após alterar o script de geração, recompile o executável.

## Threads e consulta de releases

O fluxo é obrigatório. `src/main.py` chama `Inicializador.iniciar()`, que agenda a consulta automática. O retorno só libera o painel após o resultado `atualizado`. Fechamento manual ou execução do instalador não liberam a versão antiga.

`verificar_atualizacoes()` retorna `(mensagem, status, url_download)`:

| Status | Ação do inicializador |
| --- | --- |
| `atualizado` | Agenda abertura do painel. |
| `disponivel` | Baixa automaticamente e tenta executar o arquivo. |
| `erro` | Permite tentar novamente; mantém o painel bloqueado. |

A comparação usa tuplas numéricas `MAJOR.MINOR.PATCH`, com prefixo `v` opcional. Rascunhos, pré-releases, JSON inválido, falhas HTTP ou de rede e versões novas sem asset `.exe` resultam em erro. A consulta usa timeout de 15 segundos. A versão local é `VERSAO_ATUAL` em `src/update.py`, atualmente `1.1.2`.

Consulta e download usam threads daemon e publicam resultados em uma fila. A thread principal consome os eventos a cada 100 ms e atualiza os widgets. O código impede novos downloads durante um download ativo, mas não impede consultas simultâneas (QA-01).

O download usa `urlopen` com timeout de 60 segundos, lê blocos de até 1 MiB e salva na pasta temporária do sistema. Remove o arquivo quando uma exceção interrompe a operação e rejeita arquivo vazio. Não verifica hash, assinatura ou igualdade com `Content-Length`. O timeout de rede não é um limite total da atualização.

O primeiro asset terminado em `.exe` é tratado como instalador, sem seleção por nome específico ou arquitetura. Após baixar, `os.startfile()` tenta executá-lo no Windows e o aplicativo fecha. Isso não confirma instalação bem-sucedida. O instalador precisa realizar a instalação e eventual reabertura; `criar_executavel.py` gera somente o aplicativo.

Durante o download obrigatório, fechar mostra um aviso e mantém a janela. Fora dessa etapa, encerra sem abrir o painel; resultados tardios deixam de ser consumidos. Falhas permitem tentar novamente. Mensagens de exceção do atualizador podem aparecer na interface; não há sanitização geral.

Não existem nesta cópia `gerar_launcher.py`, `criar_executavel_launcher.py` nem launcher independente na raiz. Use `python src/main.py` ou o executável principal.

As requisições usam um contexto TLS que preserva as CAs do sistema e acrescenta as do `certifi`. A validação de certificado e nome do servidor permanece habilitada. O empacotamento inclui os dados do pacote. Veja [Erro de certificado](erro-certificado.md).

Os testes locais não confirmam acesso à rede afetada, instalação real ou seletores do Conveniar. Consulte [testes e validação](testes.md) antes de distribuir.
