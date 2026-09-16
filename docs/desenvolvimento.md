# Desenvolvimento

Este guia descreve o código existente e separa as regras pretendidas das funcionalidades ainda pendentes. Consulte o [README](../README.md) para a configuração e a estrutura do projeto.

Para apoio ao estagiário, consulte o [guia básico de Git e GitHub](github-basico.md), o [atalho de commit e envio da branch atual](../ferramentas/github/README.md) e os [exemplos de componentes de interface](componentes-interface.md). Os exemplos são material de estudo; o painel definitivo continua sob responsabilidade do integrante designado.

## Responsabilidades dos módulos

| Arquivo | Responsabilidade atual |
| --- | --- |
| `src/main.py` | Instancia `Interface` e inicia o laço da interface gráfica. |
| `src/interface.py` | Cria a janela CustomTkinter e o rótulo do projeto. Contém uma rotina de login, busca e processamento ainda sem conexão com um botão. |
| `src/browser.py` | Contém as rotinas de login, consulta e download, além da função de espera do loader ainda não implementada. |
| `src/config.py` | Lê as variáveis de ambiente e define os caminhos da raiz e dos downloads. |
| `tests/test_regras.py` | Define testes de situação e normalização, mas importa um módulo ausente. |

## Integração do painel e autenticação

O painel planejado terá entrada para o número do projeto. `interface.py` será integrado separadamente pelo responsável pela interface.

O painel deve chamar `realizar_login()` sem argumentos. A rotina usa `USUARIO` e `SENHA` de `src/config.py`, que carrega o `.env` da raiz. Não há persistência de credenciais em JSON, campos de login ou opção de logout local no painel. O login continua sujeito à limitação do loader descrita abaixo.

## Consulta e situação dos contratos

`buscar_contratos(driver, numero_projeto)` contém esta sequência:

1. Selecionar `Contrato de Bolsa`.
2. Informar o número do projeto e selecionar uma opção correspondente.
3. Limpar o campo de data inicial.
4. Acionar a consulta e obter as linhas da tabela da página atual.
5. Ignorar linhas com menos de 11 colunas, de outro projeto ou sem link de contrato.
6. Retornar somente contratos cuja situação, após remoção de espaços nas extremidades e conversão para minúsculas, seja `ativo` ou `encerrado`.

A rotina não altera o filtro de situação. O requisito é consultar sem esse filtro e selecionar os contratos válidos nas linhas retornadas; não são previstas duas consultas separadas por situação.

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

- A interface não possui entrada de projeto nem botão de execução conectado.
- A busca limpa apenas a data inicial, sem limpar todos os filtros de data.
- `requirements.txt` não declara `selenium` nem `customtkinter`, apesar dos imports no código.
- O navegador depende dos caminhos fixos para Windows descritos no README.
- Não há tratamento que assegure continuar nos demais contratos após uma exceção, nem fechamento garantido das janelas em caso de falha.

Esses pontos são registros de documentação, não correções implementadas.

## Testes existentes

`pytest.ini` configura a descoberta de `test_*.py` em `tests/` e a saída reduzida com `-q`.

`tests/test_envio_github.py` valida o script de envio usando repositórios temporários e um remoto local, sem acessar o GitHub. Requer Git e PowerShell do Windows. Cobre commit e push da branch atual, reenvio sem novo commit, cancelamento, mensagem vazia, bloqueio de `.env` rastreado, ausência de branch ativa e preservação do commit após push rejeitado. Execute separadamente da suíte de regras:

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
