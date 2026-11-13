# v1.0.0 — Lançamento inicial

**Data:** 2026-09-17
**Commit:** `bcaa0d9`

## O que foi entregue

Primeira versão funcional do projeto com todos os módulos principais.

### Módulos incluídos

| Arquivo | Responsabilidade |
|---------|-----------------|
| `src/browser.py` | Autenticação no Conveniar, consulta e download de anexos |
| `src/interface.py` | Painel gráfico com campo de projeto, seleção de pasta e log de etapas |
| `src/config.py` | Leitura de `.env`, caminhos compartilhados |
| `src/main.py` | Entrada da aplicação |
| `src/update.py` | Verificação de atualizações automáticas |

### Infraestrutura

- `main.spec` — configuração do PyInstaller para gerar o `.exe`
- `criar_executavel.py` — script auxiliar de compilação
- `requirements.txt` e `requirements-build.txt` — dependências declaradas
- `icon/logo.ico` — ícone do aplicativo
- `VERSAO_CHROME.txt` — versão do Chrome compatível
- `ferramentas/github/enviar.py` — script para envio ao GitHub

### Histórico de commits desta versão

| Data | Descrição |
|------|-----------|
| 2026-09-17 | Merge pull request #4 — versão 1.0.0 |
| 2026-09-17 | Versão 1.0.0 |
| 2026-09-17 | Merge pull request #3 da branch dev |
| 2026-09-16 | feat: adicionando interface |
| 2026-09-16 | Merge pull request #2 da branch feature-config |
| 2026-09-16 | Adicionando documentação |
| 2026-09-16 | Adicionando Chrome e chromedriver |
| 2026-09-16 | Adicionando componente frame inicial |
| 2026-09-16 | Adicionando correções |
| 2026-09-16 | Adicionando o fluxo da automação |
| 2026-09-15 | Atualizando arquitetura |
| 2026-09-15 | chore: adiciona estrutura inicial do projeto |
| 2026-09-15 | Add development guidelines document |
| 2026-09-15 | Inicializando projeto |
| 2026-09-15 | Initial commit |

## Limitações conhecidas nesta versão

- Paginação não implementada
- Seletor `imgLoad` do loader ainda não validado no Conveniar
- Contratos sem tabela de anexos podiam interromper o processamento
