# v1.1.2 — Atualização automática e launcher

**Data:** 2026-09-17
**Commit:** `ef01605`

## O que mudou em relação à v1.1.1

Versão com maior conjunto de alterações desde o lançamento inicial.

### Novas funcionalidades

- **Atualização automática completa** (`src/update.py` expandido de ~41 para ~385 linhas)
  - Verifica versão no GitHub ao abrir o aplicativo
  - Bloqueia o painel até confirmar a versão ou baixar a atualização
  - Falhas na verificação mantêm o painel bloqueado com mensagem de erro
- **Launcher** (`src/launcher.py` — novo, 652 linhas)
  - Processo separado que gerencia o ciclo de vida do aplicativo principal
  - Permite reinicialização após atualização sem fechar manualmente

### Alterações em módulos existentes

| Arquivo | Tipo | Resumo |
|---------|------|--------|
| `src/browser.py` | Refatoração | Ajustes no fluxo de autenticação e download |
| `src/config.py` | Expansão | Novos caminhos e constantes de configuração (13 → 37+ linhas) |
| `src/interface.py` | Expansão | Integração com launcher e estados de atualização |
| `src/main.py` | Ajuste | Entrada adaptada para trabalhar com launcher |

### Testes adicionados

| Arquivo | O que testa |
|---------|-------------|
| `tests/test_carregamento.py` | Carregamento inicial e verificação de versão |
| `tests/test_interface_threads.py` | Thread da automação e responsividade da interface |
| `tests/test_launcher.py` | Ciclo de vida do launcher |
| `tests/test_update.py` | Lógica de atualização automática |

### Documentação

- `docs/desenvolvimento.md` expandido com detalhes do fluxo de atualização
- `passos de desenvolvimento.md` adicionado na raiz

### Histórico de commits desta versão

| Data | Commit | Descrição |
|------|--------|-----------|
| 2026-09-17 | `ef01605` | feat: implementa atualização automática da aplicação |

## Limitações conhecidas nesta versão

- Paginação ainda não implementada
- Seletor `imgLoad` do loader ainda não validado no Conveniar
- Consultas simultâneas (QA-01) documentadas como falha esperada em `docs/testes.md`
