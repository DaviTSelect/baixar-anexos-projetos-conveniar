# v1.3.0 — Interface PySide6, checkbox headless e automação mais rápida

**Data:** 2026-11-13
**Commits:** `296f47e` → `45ef250` (branch `atualizacoes`)

---

## Adicionado

- **Checkbox "Ocultar Chrome"** (Step 03 no painel)
  - Quando marcado, o navegador executa em modo headless (`--headless=new`)
  - Passa `headless=True/False` diretamente para `realizar_login()`; credenciais continuam no `.env`

## Alterado

- **Interface reescrita em PySide6** (substituindo customtkinter)
  - Janela 940×580, paleta PADRAO_EMPRESA: fundo `#203447`, ação `#e94c1f`, card `#f8f7f3`
  - Shims de compatibilidade (`_AppProxy`, `_Label`, `_Button`, `_Entry`, `_MessageBox`) mantêm a API esperada pelos testes
  - `requirements.txt`: `customtkinter` → `PySide6`

- **Automação mais rápida**
  - 8 flags de desempenho no Chrome: `--disable-background-timer-throttling`, `--disable-backgrounding-occluded-windows`, `--disable-renderer-backgrounding`, entre outros
  - Limiar de estabilidade do loader: 1 s → 0,5 s (poll 0,2 s → 0,15 s)
  - Limiar de estabilidade das linhas de contratos: 2 s → 1 s
  - Removidas 2 esperas redundantes de loader após `send_keys` no login

## Corrigido

- `fix: impede consultas simultâneas no inicializador (QA-01)` — botão bloqueado enquanto busca está em curso
- Testes de regressão atualizados para refletir os novos limiares (76/76 passando)

## Arquivos alterados

- `version.py` — atualizado para `1.3.0`
- `src/interface.py` — reescrito em PySide6 com `ToggleRow` para headless
- `src/browser.py` — flags de desempenho, limiares menores, parâmetro `headless`
- `requirements.txt` — `customtkinter` → `PySide6`
- `AGENTS.md` — restrição: `realizar_login()` aceita apenas `headless` como argumento
- `tests/test_carregamento.py`, `tests/test_downloads.py`, `tests/test_interface_threads.py` — ajuste para novos limiares
