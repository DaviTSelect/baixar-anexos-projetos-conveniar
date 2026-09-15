# Desenvolvimento

Este projeto deve permanecer simples, seguro e fácil de manter.

## Princípio

```text
Entender → Implementar → Fazer funcionar → Validar → Corrigir → Documentar
```

Não adicionar complexidade sem necessidade real.

## Divisão dos arquivos

### `main.py`

Orquestra o fluxo principal.

### `browser.py`

Concentra ações comuns do navegador, principalmente espera de loader e navegação compartilhada.

### `contratos.py`

Contém regras e operações relacionadas à busca, leitura e processamento dos contratos.

### `config.py`

Centraliza configurações e leitura das variáveis de ambiente.

## Regra de situação

A consulta é realizada sem filtro de situação.

Somente contratos `ATIVO` e `ENCERRADO` são processados.

Outras situações são ignoradas.

Essa regra deve permanecer isolada para ser simples de testar.

## Loader

Toda operação que provocar carregamento deve aguardar o loader desaparecer antes da próxima interação.

Evitar `time.sleep()` quando for possível aguardar uma condição real.

Toda espera deve possuir timeout.

## Paginação

Percorrer todas as páginas até que não exista próxima página.

Uma página sem contratos `ATIVO` ou `ENCERRADO` não significa fim da paginação.

## Downloads

Todos os anexos são armazenados em:

```text
downloads/<numero_projeto>/
```

Não sobrescrever silenciosamente arquivos existentes.

## Logs

Registrar somente informações úteis para investigação, como:

```text
[INFO] Projeto 12345
[INFO] Página 2
[INFO] Contrato 1001 - ATIVO
[INFO] 3 anexos encontrados
[INFO] Download concluído: documento.pdf
[WARNING] Contrato sem anexos
[ERROR] Falha ao abrir contrato 1005
```

Nunca registrar senha ou credenciais.

## Tratamento de erros

Priorizar erros que podem interromper ou comprometer a automação:

- login inválido;
- loader/timeout;
- falha na paginação;
- falha ao abrir contrato;
- falha no download;
- diretório não disponível;
- mudança relevante na interface.

Evitar `except: pass`.

## Testes

Não buscamos 100% de cobertura.

Testar somente regras pequenas e críticas que tragam valor.

Inicialmente:

- `ATIVO` deve ser processado;
- `ENCERRADO` deve ser processado;
- outras situações devem ser ignoradas;
- normalização de espaços/maiúsculas deve funcionar.

Novos testes devem ser adicionados quando um bug importante for encontrado ou uma nova regra de negócio justificar proteção.

## Estagiário

Foco inicial:

1. Entender o fluxo.
2. Executar a automação em cenários controlados.
3. Documentar funções relevantes.
4. Verificar comportamentos inesperados.
5. Registrar como reproduzir erros.
6. Criar testes somente para regras importantes.

A correção de erros pode ser assumida progressivamente.

## Ao encontrar um erro

Registrar:

```text
Projeto:
Página:
Contrato:
Etapa:
Esperado:
Obtido:
Como reproduzir:
Mensagem/log:
```

Se o erro representar uma regra que pode ser isolada, criar um teste antes ou junto da correção.

## Git

Fluxo simples:

```text
main
  ↓
feature/<tema>
  ↓
Pull Request
  ↓
revisão
  ↓
main
```

Branches sugeridas conforme necessário:

```text
feature/login
feature/busca-contratos
feature/download-anexos
fix/<problema>
docs/<tema>
```

Não criar todas antecipadamente.

## Commits

```text
feat: nova funcionalidade
fix: correção
test: teste relevante
docs: documentação
refactor: melhoria interna sem alterar comportamento
chore: configuração/manutenção
```

## Pull Requests sugeridos

O desenvolvimento pode ser dividido em poucos PRs:

1. Estrutura inicial e login.
2. Busca, filtros, leitura dos resultados e paginação.
3. Processamento dos contratos e downloads.
4. Ajustes finais, logs, erros e documentação.

A divisão pode mudar se uma funcionalidade ficar grande demais.
