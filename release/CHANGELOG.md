# Changelog — Baixar Anexos de Contratos por Projeto

Registro de todas as alterações, organizado por versão. Cada versão tem sua própria pasta com notas detalhadas.

---

## Versões

| Versão | Data | Pasta | Resumo |
|--------|------|-------|--------|
| Não lançado | — | [nao-lancado/](nao-lancado/NOTAS.md) | Alterações após a versão atual, sem tag |
| v1.3.0 | 2026-11-13 | [v1.3.0/](v1.3.0/NOTAS.md) | Interface PySide6, checkbox headless, automação mais rápida |
| v1.2.2 | 2026-11-04 | [v1.2.2/](v1.2.2/NOTAS.md) | Correção de falso positivo de vírus no `.exe`; mapeamento de releases |
| v1.1.2 | 2026-09-17 | [v1.1.2/](v1.1.2/NOTAS.md) | Atualização automática completa + launcher + 4 novos arquivos de teste |
| v1.1.1 | 2026-09-17 | [v1.1.1/](v1.1.1/NOTAS.md) | Versão "Projeto Final" — consolidação do estado entregável |
| v1.1.0 | 2026-09-17 | [v1.1.0/](v1.1.0/NOTAS.md) | Mesma base da v1.0.0 — tag de nomenclatura |
| v1.0.0 | 2026-09-17 | [v1.0.0/](v1.0.0/NOTAS.md) | Lançamento inicial — todos os módulos principais, interface, download e spec |

---

## Estrutura desta pasta

```
release/
├── CHANGELOG.md          ← este arquivo (índice)
├── nao-lancado/
│   └── NOTAS.md          ← alterações após a versão atual sem tag
├── v1.3.0/
│   └── NOTAS.md
├── v1.2.2/
│   └── NOTAS.md
├── v1.1.2/
│   └── NOTAS.md
├── v1.1.1/
│   └── NOTAS.md
├── v1.1.0/
│   └── NOTAS.md
└── v1.0.0/
    └── NOTAS.md
```

Ao criar uma nova tag de versão, mova o conteúdo de `nao-lancado/` para a nova pasta `vX.X.X/` e limpe `nao-lancado/NOTAS.md`.
