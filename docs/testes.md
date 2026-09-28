# Testes e validação de QA

Os testes automatizados usam dados fictícios, navegador e janelas simulados e diretórios temporários. Não leem o `.env`, não acessam o Conveniar, não baixam releases reais e não executam instaladores. Os testes de envio fazem commit e push apenas em repositórios temporários com remotos locais.

## Executar

Na raiz que contém `src/`, `tests/` e `requirements.txt`, com as dependências instaladas:

```powershell
python -B -m pytest -p no:cacheprovider
```

Git é necessário para os testes de envio; os casos PowerShell são ignorados quando esse shell não está disponível. O ambiente precisa permitir leitura, escrita e limpeza de seus diretórios temporários. Erros de permissão do ambiente devem ser registrados separadamente dos defeitos do projeto.

Para validar somente regras, atualizações e inicializador:

```powershell
python -B -m pytest tests/test_regras.py tests/test_update.py tests/test_launcher.py -p no:cacheprovider
```

## Cobertura existente

| Arquivo | Comportamentos verificados |
| --- | --- |
| `test_regras.py` | Filtragem real de situações e projeto, espaços e maiúsculas/minúsculas, ausência de link, linhas incompletas, ordem e consulta vazia. |
| `test_carregamento.py` | Linhas tardias ou substituídas, crescimento da página, tabela vazia, timeout e liberação do navegador após falha de login. |
| `test_downloads.py` | Arquivos parciais, crescimento, ambiguidade, loader tardio, vários anexos, colisões, tabela vazia ou ausente e restauração de navegação. |
| `test_interface_threads.py` | Janela responsiva, fila de eventos, execução única, fechamento cooperativo, consulta vazia, falha em contrato e encerramento do navegador. |
| `test_launcher.py` | Consulta automática, liberação do painel, atualização obrigatória, progresso, falhas, instalação simulada e fechamento. |
| `test_update.py` | Comparação numérica, respostas inválidas, ausência de instalador, erros de rede, gravação, progresso e limpeza de download interrompido ou vazio. |
| `test_update_ssl.py` | Preservação das CAs do sistema, acréscimo de certifi e manutenção da validação TLS em consultas e downloads. |
| `test_envio_github.py` | Envio local simulado, cancelamento, bloqueio de `.env`, ausência de branch e preservação de commit após push rejeitado. |

## Falha esperada: QA-01

`InicializadorTests.test_consultas_simultaneas_devem_ser_impedidas` chama `verificar()` duas vezes antes de receber um resultado. O esperado é iniciar apenas uma consulta; atualmente são iniciadas duas threads.

O teste permanece com `xfail(strict=True)`: registra uma falha conhecida sem tratá-la como comportamento correto. `XFAIL` não equivale a aprovado. Após corrigir o código, ele produzirá `XPASS` e fará a suíte falhar até remover a marcação. A atualização dos testes e documentos não corrige a automação.

Essa reprodução chama o método diretamente; não comprova que todo usuário consegue disparar duas consultas pela interface. Falta uma trava no método para impedir sobreposição.

## Limitações que não devem ser confundidas com aprovação

- Os testes de tabela ausente e de falha em contrato caracterizam o comportamento atual de interrupção; não aprovam esse comportamento como requisito definitivo.
- Não há paginação, limpeza de todos os filtros nem relatório de completude. Um teste local aprovado não comprova que todos os anexos de um projeto foram obtidos.
- Os sinais de autenticação, os seletores e o funcionamento do CDP precisam de validação no Conveniar.
- A atualização bloqueia o painel em falhas de rede. Escolhe o primeiro `.exe` e não verifica hash, assinatura ou igualdade entre bytes recebidos e tamanho anunciado.
- Testes de widgets simulados não validam aparência, escala da tela, integração real com Windows ou instalação.

## Validação manual antes de distribuir

Estes cenários são um plano; não foram executados nesta revisão. Use projetos autorizados e registre os resultados sem credenciais.

| Cenário | Evidência necessária |
| --- | --- |
| Projeto com uma página | Comparar contratos e anexos esperados com os arquivos obtidos. |
| Projeto com várias páginas | Registrar os contratos omitidos pela limitação atual; exigir coleta completa antes de aprovar esse cenário. |
| Filtros de data e situação preenchidos | Conferir se contratos válidos ficam ocultos. |
| Contrato sem anexos | Testar tabela vazia e ausência da tabela, registrando eventual interrupção. |
| Anexos diferentes com mesmo nome | Confirmar que a regra atual preserva o existente e registrar a perda do segundo conteúdo no resultado. |
| Login inválido e sessão expirada | Registrar em qual etapa o erro aparece e confirmar encerramento do navegador. |
| Falha de rede durante download | Verificar arquivo parcial, mensagem e contratos que não foram processados. |
| Fechar durante processamento | Confirmar que a janela aguarda a operação atual e encerra o navegador. |
| Atualização disponível, ausente ou indisponível | Conferir bloqueio/liberação do painel, download, instalador publicado e reabertura da versão correta. |

Registre versão/commit, cenário, resultado esperado, resultado obtido e evidências. Separe aprovação dos testes locais da aprovação do fluxo completo. Para uso sem acompanhamento, o aplicativo deve concluir a coleta inteira ou informar claramente tudo que ficou pendente.
