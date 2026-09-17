# Desenvolvimento

Este guia descreve o código existente e separa as regras pretendidas das funcionalidades ainda pendentes. Consulte o [README](../README.md) para a configuração e a estrutura do projeto.

Para apoio ao estagiário, consulte o [guia básico de Git e GitHub](github-basico.md), o [atalho de commit e envio da branch atual](../ferramentas/github/README.md) e os [exemplos de componentes de interface](componentes-interface.md). Os exemplos são material de estudo; o painel definitivo continua sob responsabilidade do integrante designado.

## Responsabilidades dos módulos

| Arquivo | Responsabilidade atual |
| --- | --- |
| `src/main.py` | Instancia `Interface` e inicia o laço da interface gráfica. |
| `src/interface.py` | Cria a janela CustomTkinter, recebe o projeto e a pasta, inicia a automação e mostra o contrato em processamento. |
| `src/browser.py` | Contém as rotinas de login, consulta e download, além da função de espera do loader ainda não implementada. |
| `src/config.py` | Lê as variáveis de ambiente e define os caminhos da raiz e dos downloads. |
| `tests/test_regras.py` | Define testes de situação e normalização, mas importa um módulo ausente. |

## Integração do painel e autenticação

O painel possui entrada para o número do projeto, seleção de pasta e botão de execução. O rótulo de status mostra login, consulta e `Baixando anexos do contrato <número>...` antes de processar cada contrato. Ao terminar, indica conclusão, ausência de contratos ou a etapa que falhou.

O texto é redesenhado com `update_idletasks()` antes das chamadas do Selenium. A execução continua síncrona: o rótulo identifica o contrato em processamento, mas não mede o progresso dos arquivos, e a janela ainda pode ficar sem responder durante esperas longas. O botão fica desabilitado durante o processamento; o navegador retornado pelo login é encerrado ao final, inclusive em falhas.

O painel deve chamar `realizar_login()` sem argumentos. A rotina usa `USUARIO` e `SENHA` de `src/config.py`, que carrega o `.env` da raiz. Não há persistência de credenciais em JSON, campos de login ou opção de logout local no painel. O login continua sujeito à limitação do loader descrita abaixo.

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

`aguardar_loader_desaparecer(page, timeout=30)` ainda lança `NotImplementedError`. Embora as rotinas a chamem, não há espera efetiva pelo loader, e essas chamadas interrompem a execução.

O requisito é aguardar uma condição real da página com timeout após operações que provoquem carregamento. O código também contém esperas fixas com `time.sleep()`.

A paginação ainda não foi implementada. As chamadas para rolar a página não constituem navegação entre páginas de resultados.

Quando implementada, a paginação deverá:

- Percorrer todas as páginas, inclusive as que não tenham contratos válidos.
- Evitar processar uma página duas vezes ou ignorar a última.
- Preservar a navegação ao retornar dos detalhes de um contrato.
- Evitar laços infinitos.

## Processamento e downloads

A sequência presente em `processar_contrato(driver, item, projeto)`, atualmente bloqueada pelas chamadas ao loader, é:

1. Criar `downloads/<projeto>/<contrato>/`, substituindo `/` por `_` no contrato.
2. Guardar a janela atual, clicar no link e selecionar a última janela do navegador.
3. Abrir a aba `Arquivos` e localizar a tabela de anexos.
4. Coletar o primeiro botão `Baixar arquivo` de cada linha que tenha esse botão.
5. Acionar cada download e procurar um novo arquivo em `downloads/`, ignorando a extensão `.crdownload`.
6. Mover o arquivo para a pasta do contrato, se o nome ainda não existir no destino.
7. Fechar a janela do contrato e retornar à anterior.

A espera pelo arquivo usa até 120 verificações, com intervalos de um segundo. Se nenhum arquivo for identificado, a rotina lança `TimeoutError`.

Se o nome já existir no destino, o arquivo existente é mantido e o novo download é excluído. Não há comparação de conteúdo nem renomeação com sufixos. Arquivos de mesmo nome podem ter conteúdos diferentes; essa limitação deve ser considerada ao avaliar os resultados.

Se a tabela existir, mas não tiver botões de download, o laço de downloads fica vazio. Se a tabela não aparecer, a espera pode falhar por timeout. Portanto, o requisito de continuar após qualquer contrato sem anexos ainda não está plenamente atendido.

## Limitações conhecidas

Além do loader e da paginação:

- A automação executa na mesma thread da interface e bloqueia a interação durante as chamadas do Selenium.
- A busca limpa apenas a data inicial, sem limpar todos os filtros de data.
- O navegador depende dos caminhos fixos para Windows descritos no README.
- Não há tratamento que assegure continuar nos demais contratos após uma exceção, nem fechamento garantido das janelas em caso de falha.

Esses pontos são registros de documentação, não correções implementadas.

## Testes existentes

`pytest.ini` configura a descoberta de `test_*.py` em `tests/` e a saída reduzida com `-q`.

`tests/test_envio_github.py` valida as versões Python (`ferramentas/github/enviar.py`) e PowerShell do script de envio usando repositórios temporários e um remoto local, sem acessar o GitHub. Requer Git; os cenários PowerShell são ignorados quando ele não está disponível. O atalho `enviar.cmd` executa a versão Python, que usa somente a biblioteca padrão. Cobre commit e push da branch atual, reenvio sem novo commit, cancelamento, mensagem vazia, bloqueio de `.env` rastreado, ausência de branch ativa e preservação do commit após push rejeitado. Execute separadamente da suíte de regras:

```powershell
python -B -m pytest tests/test_envio_github.py -p no:cacheprovider
```

`tests/test_regras.py` define estes cenários:

- Aceitar `ATIVO` e `ENCERRADO`.
- Rejeitar `CANCELADO` e `SUSPENSO`.
- Normalizar espaços nas extremidades e diferenças entre maiúsculas e minúsculas.

Porém, o arquivo importa `normalizar_situacao` e `situacao_valida` de `src.contratos`, que não existe no código-fonte atual. Essa dependência impede a coleta dos testes em um ambiente limpo. Os testes não validam diretamente a filtragem presente em `browser.py`.

Para futuras alterações de código autorizadas, priorizar testes de regras críticas: seleção dos contratos, colisões de nomes, paginação e timeouts. Não buscar cobertura artificial nem apresentar cenários planejados como testes já existentes.

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

O script [criar_executavel.py](../criar_executavel.py) usa PyInstaller no Windows para gerar `dist/AnexosConveniar.exe` em arquivo único, sem console. Instale as dependências de [requirements-build.txt](../requirements-build.txt) antes de executar o script. Ele usa caminhos relativos à sua própria localização, podendo ser chamado de outro diretório.

O ícone é incorporado tanto ao arquivo executável quanto como recurso da janela. Os dados do CustomTkinter também são incluídos. A localização dos recursos usa `sys._MEIPASS` quando empacotado; a configuração externa usa a pasta de `sys.executable`, conforme a [documentação do PyInstaller](https://pyinstaller.org/en/stable/runtime-information.html).

O `.env` deve ficar ao lado do executável; em execução pelo código-fonte, continua na raiz do repositório. O script não copia nem incorpora credenciais, Chrome ou ChromeDriver. Não é necessário distribuir a pasta `icon` separadamente.

Cada compilação atualiza o executável de mesmo nome em `dist/`; feche o programa antes de recompilar. Os arquivos intermediários e o spec gerado ficam em `build/`, preservando o `main.spec` preexistente. `build/` e `dist/` são ignorados pelo Git. Use o script como procedimento de compilação; o `main.spec` antigo aponta para outro nome de ícone.

O empacotamento não valida login, seletores nem downloads no Conveniar. As descrições anteriores da interface e automação ainda precisam ser reconciliadas com as alterações locais feitas pela equipe.
