# Baixar Anexos de Contratos de Bolsistas por Projeto

Automação interna do setor de projetos para baixar os anexos dos contratos de bolsistas vinculados a um projeto.

**Prioridade:** 2  
**Status:** Em desenvolvimento

## Objetivo

A automação deverá:

1. Realizar login.
2. Acessar a busca de contratos.
3. Selecionar `Contrato de Bolsas`.
4. Limpar os filtros de data.
5. Informar o número do projeto.
6. Realizar a consulta sem filtro de situação.
7. Percorrer todas as páginas dos resultados.
8. Ler a situação de cada linha.
9. Processar somente contratos `ATIVO` ou `ENCERRADO`.
10. Ignorar as demais situações.
11. Abrir cada contrato válido.
12. Acessar `Arquivos`.
13. Localizar `Anexos`.
14. Baixar todos os documentos.
15. Salvar os arquivos em `downloads/<numero_projeto>/`.

## Fluxo

```text
Login
  ↓
Busca de contratos
  ↓
Contrato de Bolsas
  ↓
Limpar datas
  ↓
Informar projeto
  ↓
Buscar sem filtro de situação
  ↓
Percorrer todas as páginas
  ↓
Para cada linha:
  ├── ATIVO → processar
  ├── ENCERRADO → processar
  └── outro → ignorar
  ↓
Abrir contrato
  ↓
Arquivos → Anexos
  ↓
Baixar documentos
  ↓
downloads/<projeto>/
```

## Regras importantes

- Nunca versionar `.env`.
- Não registrar senhas nos logs.
- Aguardar o loader antes de interagir novamente com a página.
- Utilizar timeout para evitar travamentos indefinidos.
- Um contrato sem anexos não deve encerrar toda a execução.
- Não sobrescrever silenciosamente arquivos com o mesmo nome.
- Continuar a paginação mesmo quando uma página não possuir contratos válidos.

## Estrutura

```text
baixar-anexos-projetos-conveniar/
├── src/
│   ├── main.py
│   ├── browser.py
│   ├── contratos.py
│   └── config.py
├── tests/
│   └── test_regras.py
├── docs/
│   └── desenvolvimento.md
├── downloads/
│   └── .gitkeep
├── .github/
│   └── PULL_REQUEST_TEMPLATE.md
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

## Desenvolvimento

Consulte `docs/desenvolvimento.md` para o fluxo de trabalho, testes essenciais e orientações para manutenção.
