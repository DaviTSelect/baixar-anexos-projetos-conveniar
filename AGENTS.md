# Regras para agentes e colaboradores

Estas instruções se aplicam a todo o repositório. Antes de trabalhar, leia este arquivo, o [README](README.md) e as seções pertinentes do [guia de desenvolvimento](docs/desenvolvimento.md).

## Comunicação e dúvidas

- Comunique-se em português, de forma clara e objetiva.
- Siga as instruções mais recentes do usuário. Se elas alterarem uma regra deste arquivo, atualize a documentação afetada.
- Pergunte quando houver dúvida que altere o objetivo, uma regra de negócio, a responsabilidade de outro integrante ou o efeito de uma ação irreversível.
- Não invente requisitos, seletores do Conveniar ou resultados de testes. Informe o que ainda não foi confirmado.
- Resolva escolhas pequenas e reversíveis de implementação com base no código e nas regras existentes, sem pedir confirmação a cada passo.
- Ao concluir, informe o que mudou, como foi verificado e quais limitações permanecem.

## Escopo e preservação do trabalho

- Verifique o estado do Git antes de editar e preserve alterações preexistentes de outros colaboradores.
- Faça somente as mudanças necessárias ao pedido. Evite refatorações, dependências e abstrações sem necessidade concreta.
- Em pedidos restritos à documentação, não altere código ou configuração para corrigir problemas encontrados; registre-os.
- Ao desfazer uma implementação, remova apenas as alterações relacionadas ao que foi solicitado.
- Não descarte alterações, sobrescreva trabalho alheio nem apague arquivos sem relação com a tarefa.
- Não faça commit, push, merge ou publicação sem solicitação do usuário.

## Autenticação e configuração

- O login usa `USUARIO` e `SENHA` configurados no `.env`, carregados por `src/config.py`.
- A interface deve chamar `realizar_login()` sem argumentos.
- Não implemente login local, armazenamento de credenciais em JSON, opção de lembrar senha ou campos de usuário e senha no painel, salvo nova solicitação explícita.
- Não coloque credenciais diretamente no código, na documentação, em testes, logs ou mensagens de erro.
- Não versione `.env` ou arquivos com credenciais. Use somente valores fictícios no `.env.example` e nos testes.
- Evite ler ou imprimir o conteúdo do `.env` quando a tarefa puder ser realizada consultando `src/config.py` e `.env.example`.
- `HEADLESS` controla o navegador, não a janela gráfica. Mantenha essa distinção na documentação.

## Interface e componentes

- O painel definitivo está sendo desenvolvido por outro integrante da equipe.
- Não substitua ou amplie o painel definitivo sem pedido que inclua esse trabalho.
- Se uma interface temporária de testes for solicitada, mantenha-a separada de `src/interface.py`, com execução explícita e instruções de remoção.
- Um painel temporário não deve se tornar a entrada padrão da aplicação sem solicitação.
- A entrada prevista no painel é o número do projeto; a autenticação permanece no `.env`.

## Organização do código

- `src/main.py`: entrada da aplicação e inicialização da interface.
- `src/interface.py`: componentes gráficos e eventos da interface.
- `src/browser.py`: autenticação no Conveniar, consulta, navegação e download.
- `src/config.py`: leitura da configuração e definição dos caminhos compartilhados.
- Separe regras de negócio dos componentes visuais quando houver necessidade real; não crie módulos apenas para completar uma estrutura sugerida.
- Antes de alterar uma função, verifique sua implementação, seus chamadores e os testes relacionados.
- Prefira funções com responsabilidade clara e comentários que expliquem decisões relevantes.

## Regras da automação

As regras abaixo descrevem o comportamento pretendido. Consulte o guia para distinguir o que já está implementado.

- Consultar contratos do tipo `Contrato de Bolsa` para o projeto informado.
- Limpar os filtros de data e consultar sem filtro de situação.
- Processar somente contratos `ATIVO` ou `ENCERRADO`, normalizando espaços e diferenças de maiúsculas/minúsculas.
- Ignorar contratos de outro projeto, outras situações e linhas sem link válido.
- Percorrer todas as páginas, inclusive páginas sem contratos válidos, sem repetir páginas ou entrar em laços infinitos.
- Aguardar condições reais da página com timeout após ações que provoquem carregamento. Não substituir a espera do loader por pausas fixas como solução definitiva.
- Confirmar seletores e sinais de autenticação no sistema antes de tratá-los como confiáveis. Uma mensagem no console não comprova login válido.
- Preservar a navegação ao retornar dos detalhes de um contrato.
- Organizar anexos em `downloads/<numero_projeto>/<contrato>/`, substituindo `/` por `_` no número do contrato.
- Não sobrescrever silenciosamente arquivos existentes. O comportamento atual mantém o arquivo existente e descarta o novo de mesmo nome, sem comparar conteúdo; não altere essa regra sem esclarecer o comportamento desejado.
- Confirmar a conclusão de cada download com timeout antes de mover o arquivo.
- Contratos sem anexos não devem impedir o processamento dos demais. Não apresente esse requisito como plenamente implementado enquanto os casos de ausência de tabela não forem tratados.
- Trate erros de forma que permitam identificar a etapa da falha, sem expor credenciais. Ao implementar novos fluxos, assegure o encerramento dos recursos de navegador sob sua responsabilidade.

## Verificação e testes

- Execute verificações proporcionais ao que mudou. Não execute login real ou downloads para validar alterações apenas documentais.
- Use dados fictícios e diretórios temporários nos testes automatizados.
- Priorize testes de regras críticas e regressões: seleção de contratos, paginação, colisões de nomes, timeouts e tratamento de falhas.
- Não crie testes que apenas repitam a implementação nem busque cobertura artificial.
- Não declare sucesso de execução ou de integração sem evidência. Diferencie revisão estática, testes automatizados e validação real no Conveniar.
- Registre bloqueios existentes separadamente de falhas introduzidas pela alteração.
- Antes de concluir, revise o diff, verifique problemas de formatação com `git diff --check` e confira que nenhum segredo ou artefato temporário foi incluído.

## Documentação

- Mantenha o README como visão geral, configuração e estado atual do projeto.
- Centralize os detalhes técnicos em `docs/desenvolvimento.md`; `desenvolvimento.md` da raiz direciona para esse guia.
- Atualize a documentação quando mudar comportamento, configuração, dependências ou forma de execução.
- Diferencie explicitamente funcionalidades implementadas, requisitos futuros e limitações conhecidas.
- Remova referências a módulos excluídos e confira links locais e blocos de código Markdown.
- Use o [modelo de pull request](.github/PULL_REQUEST_TEMPLATE.md) quando a tarefa incluir a criação de um PR. Descreva a mudança final, a validação realizada e as limitações relevantes.

## Limitações atuais a conferir antes de trabalhar

- A interface está conectada à automação e mostra o contrato em processamento; as chamadas do Selenium ainda bloqueiam a interação com a janela.
- A espera do loader lança `NotImplementedError`.
- A consulta não implementa paginação e limpa apenas a data inicial.
- `tests/test_regras.py` importa `src.contratos`, que ainda não existe.
- O navegador depende dos caminhos de Chrome e ChromeDriver para Windows descritos no README.

Esta lista não autoriza correções fora do pedido. Atualize-a quando uma dessas limitações for resolvida.
