# Baixar Anexos de Contratos de Bolsistas por Projeto

Automação responsável por localizar contratos de bolsistas vinculados a um projeto e baixar todos os documentos disponíveis na seção **Arquivos → Anexos** de cada contrato.

**Prioridade:** 2
**Status:** Em desenvolvimento

## Objetivo

Automatizar o processo manual de consulta e download dos anexos dos contratos de bolsas.

A automação deverá:

1. Realizar login no sistema.
2. Acessar a página de busca de contratos.
3. Configurar os filtros da consulta.
4. Localizar os contratos do projeto informado.
5. Processar contratos **ativos** e **encerrados**.
6. Percorrer todas as páginas de resultados.
7. Entrar individualmente em cada contrato.
8. Acessar a aba **Arquivos**.
9. Localizar a seção **Anexos**.
10. Baixar todos os documentos disponíveis.

---

# Fluxo da automação

## 1. Login

Realizar o login no sistema utilizando as credenciais configuradas para a automação.

As credenciais não devem ser armazenadas diretamente no código.

Exemplo:

```text
.env
```

O arquivo `.env` deve estar incluído no `.gitignore`.

Após o login, validar se a autenticação foi concluída antes de continuar.

---

## 2. Acessar busca de contratos

Após autenticar:

1. Entrar na página de busca de contratos.
2. Aguardar o carregamento completo da página.
3. Confirmar que não existe loader de carregamento bloqueando a interface.

---

## 3. Configurar filtros

Na tela de busca:

### Tipo de contrato

Selecionar:

```text
Contrato de Bolsas
```

### Datas

Limpar os campos de data existentes.

A busca não deverá ficar limitada por uma data previamente preenchida pelo sistema.

### Projeto

Selecionar/utilizar o filtro de projeto e informar o número do projeto recebido pela automação.

Exemplo:

```text
12345
```

Evitar manter o número do projeto fixo no código.

---

# 4. Buscar contratos

A automação deverá executar o procedimento para dois estados:

```text
ATIVO
ENCERRADO
```

Fluxo esperado:

```text
Projeto
   │
   ├── Contratos ativos
   │      ├── contrato 1
   │      ├── contrato 2
   │      └── ...
   │
   └── Contratos encerrados
          ├── contrato 1
          ├── contrato 2
          └── ...
```

Não assumir que os resultados estarão somente na primeira página.

---

# 5. Paginação

Depois de realizar uma busca, verificar se existem outras páginas de resultados.

A automação deverá processar:

```text
Página 1
Página 2
Página 3
...
Última página
```

Todos os contratos encontrados devem ser considerados.

O processamento somente poderá terminar quando não existirem mais páginas pendentes.

---

# 6. Processamento de cada contrato

Para cada contrato encontrado:

1. Abrir o contrato.
2. Aguardar o carregamento.
3. Acessar **Arquivos**.
4. Aguardar o carregamento.
5. Localizar a seção **Anexos**.
6. Identificar os documentos disponíveis.
7. Baixar todos os anexos.
8. Confirmar, quando possível, que o download foi concluído.
9. Retornar para continuar o processamento dos demais contratos.

A ausência de anexos não deve necessariamente interromper toda a automação.

---

# Controle de loader

Durante o desenvolvimento deverá existir uma função centralizada responsável por verificar se o loader de carregamento desapareceu antes de a automação interagir com a página.

Exemplo conceitual:

```python
def aguardar_loader_desaparecer(page):
    """
    Aguarda até que o indicador de carregamento da página
    deixe de bloquear a interface.
    """
```

Sempre que uma operação provocar carregamento da interface, utilizar essa função antes da próxima interação relevante.

Exemplo:

```text
clicar
   ↓
aguardar loader
   ↓
interagir
   ↓
clicar
   ↓
aguardar loader
   ↓
continuar
```

Evitar resolver carregamentos com esperas fixas como:

```python
time.sleep(5)
```

quando for possível aguardar diretamente uma condição da interface.

---

# Estrutura sugerida

A estrutura poderá evoluir durante o desenvolvimento, mas uma separação inicial possível é:

```text
baixar-anexos-projetos-conveniar/
│
├── src/
│   ├── login.py
│   ├── contratos.py
│   ├── anexos.py
│   ├── loader.py
│   ├── config.py
│   └── main.py
│
├── tests/
│   ├── test_contratos.py
│   ├── test_anexos.py
│   └── test_loader.py
│
├── docs/
│   └── desenvolvimento.md
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

A estrutura não deve ser seguida de maneira artificial. Caso uma responsabilidade cresça, ela poderá ser separada em novos módulos.

---

# Responsabilidades das funções

Evitar concentrar toda a automação em uma única função.

Prefira funções com uma responsabilidade clara.

Exemplos conceituais:

```python
fazer_login()

abrir_busca_contratos()

limpar_filtros_data()

selecionar_tipo_contrato()

selecionar_projeto()

buscar_contratos()

obter_contratos_da_pagina()

ir_para_proxima_pagina()

abrir_contrato()

abrir_aba_arquivos()

obter_anexos()

baixar_anexo()

aguardar_loader_desaparecer()
```

Os nomes definitivos deverão refletir a implementação real.

---

# Tratamento de erros

O tratamento de erros faz parte do desenvolvimento, mas não deve impedir a construção inicial do fluxo principal.

Primeiro devemos garantir que o caminho principal funcione:

```text
login
→ busca
→ filtros
→ contratos
→ paginação
→ arquivos
→ anexos
→ download
```

Depois serão fortalecidos cenários como:

* falha no login;
* projeto inexistente;
* nenhum contrato encontrado;
* contrato sem anexos;
* falha ao abrir contrato;
* loader que não desaparece;
* timeout;
* falha de download;
* mudança inesperada na página;
* elementos não encontrados;
* retorno incorreto após processar um contrato.

Os erros devem gerar informações suficientes para investigação.

Evitar:

```python
try:
    ...
except:
    pass
```

Uma falha não deve simplesmente desaparecer.

---

# Logs

Registrar acontecimentos relevantes durante a execução.

Exemplo:

```text
[INFO] Login realizado
[INFO] Projeto 12345 selecionado
[INFO] Buscando contratos ATIVOS
[INFO] 18 contratos encontrados
[INFO] Processando contrato 4/18
[INFO] 3 anexos encontrados
[INFO] Download concluído
[WARNING] Contrato sem anexos
[ERROR] Não foi possível abrir o contrato
```

Nunca registrar senhas ou outras credenciais.

---

# Testes

As funções deverão ser construídas pensando em testabilidade.

Sempre que uma nova função contendo regra ou transformação relevante for criada, avaliar a necessidade de criar ou atualizar seu teste.

Exemplos:

```text
função criada
      ↓
entender entrada
      ↓
entender saída
      ↓
identificar comportamento esperado
      ↓
identificar casos de erro
      ↓
criar testes
```

Não testar somente o cenário perfeito.

Por exemplo, para uma função que trata uma lista de contratos, considerar:

```text
lista com contratos
lista vazia
contrato com dados incompletos
status inesperado
dados duplicados
```

Funções que dependem diretamente do navegador podem exigir mocks, fixtures ou testes de integração. Não é necessário transformar cada clique do navegador em um teste unitário.

---

# Orientações para o estagiário

O objetivo não é apenas contribuir com código. É importante entender **por que a automação funciona**.

As principais responsabilidades serão:

### Documentação e comentários

Documentar funções importantes utilizando docstrings.

Exemplo:

```python
def obter_contratos(dados):
    """
    Processa os dados retornados pela consulta de contratos.

    Args:
        dados: Dados obtidos na consulta.

    Returns:
        Contratos válidos encontrados.
    """
```

Comentários devem explicar decisões que não são óbvias.

Evitar comentários desnecessários:

```python
# incrementa contador
contador += 1
```

Preferir documentar o motivo de determinada decisão:

```python
# A consulta pode retornar o mesmo contrato em páginas diferentes,
# portanto os IDs já processados são ignorados.
```

### Testes

Ao encontrar uma função nova:

1. Entender o objetivo da função.
2. Identificar sua entrada.
3. Identificar sua saída.
4. Criar um cenário normal.
5. Criar pelo menos um cenário de borda quando fizer sentido.
6. Executar os testes.
7. Investigar qualquer comportamento diferente do esperado.

Não alterar a implementação apenas para fazer um teste passar sem antes entender o motivo da falha.

### Verificação de erros

Durante os testes da automação, observar principalmente:

* comportamento inesperado;
* elementos que não foram encontrados;
* páginas que não carregaram;
* contratos ignorados;
* anexos que não foram baixados;
* downloads duplicados;
* erros sem mensagens claras.

Ao encontrar um problema, registrar:

```text
O que aconteceu?
Em qual etapa?
Qual era o comportamento esperado?
Qual foi o comportamento obtido?
É possível reproduzir?
Existe mensagem de erro/log?
```

Não é obrigatório resolver imediatamente todos os problemas encontrados. Primeiro é importante conseguir descrevê-los e reproduzi-los.

---

# Divisão inicial do trabalho

## Desenvolvimento principal

Responsável por:

* arquitetura da automação;
* login;
* navegação;
* filtros;
* consulta dos contratos;
* paginação;
* processamento dos contratos;
* download dos anexos;
* controle do loader;
* decisões técnicas principais.

## Estagiário

Foco inicial:

* entender o fluxo da automação;
* executar e acompanhar o sistema;
* documentar módulos e funções;
* melhorar comentários quando necessário;
* criar e manter testes;
* verificar comportamentos inesperados;
* registrar erros encontrados;
* aprender a reproduzir problemas.

A correção de erros poderá ser feita gradualmente conforme houver domínio suficiente do código.

---

# Critérios de conclusão

A automação será considerada funcional quando conseguir:

* [ ] realizar login;
* [ ] acessar a busca de contratos;
* [ ] selecionar **Contrato de Bolsas**;
* [ ] remover os filtros de data;
* [ ] consultar um projeto informado;
* [ ] buscar contratos ativos;
* [ ] buscar contratos encerrados;
* [ ] percorrer todas as páginas;
* [ ] acessar todos os contratos encontrados;
* [ ] acessar **Arquivos**;
* [ ] localizar **Anexos**;
* [ ] baixar todos os anexos;
* [ ] aguardar corretamente os loaders;
* [ ] continuar quando um contrato não possuir anexos;
* [ ] gerar logs úteis;
* [ ] possuir testes para as regras relevantes;
* [ ] possuir documentação suficiente para manutenção.

---

# Regra de desenvolvimento

O projeto deverá priorizar:

**código simples → código funcionando → testes → tratamento de erros → melhoria/refatoração**

Evitar adicionar complexidade antes de existir necessidade real.

O código deve ser escrito de forma que outro desenvolvedor consiga abrir o projeto, entender o fluxo e realizar manutenção sem depender exclusivamente de quem criou a automação.
