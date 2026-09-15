# Baixar Anexos de Contratos de Bolsistas por Projeto

Automação responsável por localizar contratos de bolsistas vinculados a um projeto e baixar todos os documentos disponíveis na seção **Arquivos → Anexos**.

A automação realiza uma única consulta por projeto e percorre todos os contratos retornados, processando somente aqueles cuja situação seja:

* **ATIVO**
* **ENCERRADO**

Contratos em outras situações deverão ser ignorados.

Todos os documentos encontrados serão armazenados em uma pasta correspondente ao projeto informado.

**Prioridade:** 2
**Status:** Em desenvolvimento

---

# 1. Objetivo

Automatizar o processo manual de consulta e download dos anexos dos contratos de bolsas vinculados a determinado projeto.

A automação deverá:

1. Realizar login no sistema.
2. Acessar a página de busca de contratos.
3. Selecionar **Contrato de Bolsas** como tipo de contrato.
4. Limpar os campos de data.
5. Informar o projeto.
6. Não aplicar filtro de situação.
7. Executar a busca.
8. Percorrer todas as páginas dos resultados.
9. Verificar a situação de cada contrato.
10. Processar somente contratos **ATIVO** ou **ENCERRADO**.
11. Ignorar contratos em outras situações.
12. Entrar individualmente em cada contrato válido.
13. Acessar **Arquivos**.
14. Localizar a seção **Anexos**.
15. Identificar todos os documentos disponíveis.
16. Baixar todos os anexos.
17. Salvar os documentos na pasta correspondente ao projeto.
18. Evitar sobrescrever arquivos silenciosamente.
19. Registrar informações relevantes da execução.

---

# 2. Fluxo geral

```text id="l8f5i1"
Iniciar
   ↓
Informar projeto
   ↓
Criar pasta do projeto
   ↓
Login
   ↓
Busca de contratos
   ↓
Tipo = Contrato de Bolsas
   ↓
Limpar campos de data
   ↓
Projeto = projeto informado
   ↓
Situação = SEM FILTRO
   ↓
Buscar
   ↓
Percorrer página
   ↓
Para cada linha:
       ↓
   Ler situação
       ↓
   ┌───────────────────────────┐
   │ ATIVO ou ENCERRADO?       │
   └───────────────────────────┘
       │                 │
      SIM               NÃO
       │                 │
       ↓                 ↓
   Processar          Ignorar
   contrato           contrato
       │
       ↓
   Arquivos
       ↓
   Anexos
       ↓
   Baixar documentos
       ↓
   Pasta do projeto
       ↓
Próxima linha
       ↓
Existe próxima página?
       │
   ┌───┴───┐
  SIM     NÃO
   │        │
   ↓        ↓
Próxima   Finalizar
página
```

---

# 3. Login

Realizar o login utilizando as credenciais configuradas para a automação.

As credenciais não deverão ficar diretamente no código.

Utilizar variáveis de ambiente:

```text id="z5dxl3"
.env
```

Exemplo:

```text id="7y3o8x"
USUARIO=...
SENHA=...
```

O `.env` deverá estar no `.gitignore`.

Nunca enviar credenciais reais para o GitHub.

Após o login, validar se a autenticação foi realizada corretamente antes de continuar.

---

# 4. Acessar a busca de contratos

Após o login:

1. Acessar a página de busca de contratos.
2. Aguardar o carregamento.
3. Garantir que o loader desapareceu.
4. Confirmar que os campos necessários estão disponíveis.
5. Iniciar a configuração dos filtros.

---

# 5. Configurar os filtros

## 5.1 Tipo de contrato

Selecionar:

```text id="9e1mdq"
Contrato de Bolsas
```

---

## 5.2 Datas

Limpar os campos de data.

A consulta não deverá ficar limitada por datas preenchidas anteriormente ou automaticamente pelo sistema.

---

## 5.3 Projeto

Informar o número do projeto recebido pela automação.

Exemplo:

```text id="xpd0yi"
12345
```

O projeto não deverá ficar fixo no código.

A mesma automação deverá conseguir processar diferentes projetos.

---

## 5.4 Situação

Não aplicar filtro de situação.

A consulta deverá retornar os contratos disponíveis para o projeto.

A situação será analisada posteriormente em cada linha dos resultados.

---

# 6. Executar a busca

Depois de configurar os filtros:

```text id="m9brgj"
Tipo = Contrato de Bolsas
Projeto = 12345
Datas = vazias
Situação = sem filtro
```

executar a busca.

Após solicitar a consulta:

```text id="izod95"
Buscar
   ↓
Aguardar loader
   ↓
Resultados disponíveis
```

Não iniciar a leitura da tabela enquanto o loader estiver bloqueando a interface.

---

# 7. Filtragem dos resultados

A regra de situação será aplicada sobre os resultados da consulta.

Para cada linha:

```text id="os6ijm"
Obter situação
      ↓
Normalizar valor
      ↓
ATIVO ou ENCERRADO?
      │
  ┌───┴────┐
 SIM      NÃO
  │         │
  ↓         ↓
Processar  Ignorar
```

Situações permitidas:

```python id="q2sn0x"
SITUACOES_PERMITIDAS = {
    "ATIVO",
    "ENCERRADO",
}
```

Exemplo conceitual:

```python id="i52dvp"
if situacao in SITUACOES_PERMITIDAS:
    processar_contrato(contrato)
```

Outra possibilidade:

```python id="zwvdbp"
if situacao not in SITUACOES_PERMITIDAS:
    continue

processar_contrato(contrato)
```

---

# 8. Normalização da situação

Sempre que possível, evitar depender exatamente de maiúsculas/minúsculas ou espaços extras retornados pela interface.

Conceitualmente:

```python id="9y0e56"
situacao = situacao.strip().upper()
```

Assim:

```text id="o7oqpf"
"Ativo"
"ATIVO"
" ativo "
```

podem ser tratados de forma consistente.

A implementação definitiva dependerá de como os valores são retornados pela página.

---

# 9. Contratos que devem ser ignorados

Qualquer situação diferente das situações permitidas deverá ser ignorada.

Exemplo:

```text id="qejx3u"
ATIVO       → PROCESSAR
ENCERRADO   → PROCESSAR

CANCELADO   → IGNORAR
SUSPENSO    → IGNORAR
PENDENTE    → IGNORAR
OUTRO       → IGNORAR
```

Ignorar um contrato não deverá ser considerado erro.

Opcionalmente, registrar:

```text id="4sxf5d"
[DEBUG] Contrato ignorado. Situação: CANCELADO
```

---

# 10. Paginação

A automação deverá percorrer **todas as páginas da consulta**.

Nunca assumir que todos os contratos estarão na primeira página.

Fluxo:

```text id="gczh9x"
Página 1
   ↓
Ler linhas
   ↓
Processar contratos válidos
   ↓
Existe próxima página?
   │
  SIM
   ↓
Página 2
   ↓
Ler linhas
   ↓
Processar contratos válidos
   ↓
...
   ↓
Última página
   ↓
Finalizar
```

Deverão ser considerados:

* consulta com uma única página;
* consulta com várias páginas;
* botão de próxima página desabilitado;
* última página;
* páginas sem contratos válidos;
* retorno à listagem após acessar um contrato;
* possibilidade de processamento duplicado;
* possibilidade de loop infinito.

---

# 11. Processamento de cada contrato

Quando a situação for válida:

```text id="8msj0j"
ATIVO
ou
ENCERRADO
```

processar o contrato.

Fluxo:

```text id="sg08bd"
Abrir contrato
      ↓
Aguardar loader
      ↓
Validar carregamento
      ↓
Abrir "Arquivos"
      ↓
Aguardar loader
      ↓
Localizar "Anexos"
      ↓
Identificar documentos
      ↓
Baixar documentos
      ↓
Confirmar downloads
      ↓
Retornar à consulta
```

Um contrato sem anexos não deverá interromper a automação.

---

# 12. Controle de loader

O controle de loader deverá ser centralizado.

Criar uma função responsável por garantir que o carregamento terminou antes da próxima interação.

Exemplo conceitual:

```python id="r3c6fp"
def aguardar_loader_desaparecer(page):
    """
    Aguarda até que o indicador de carregamento deixe
    de bloquear a interface.
    """
```

Utilizar após ações que possam provocar carregamento.

Exemplos:

```text id="glmqsc"
Login
   ↓
aguardar_loader_desaparecer()

Buscar
   ↓
aguardar_loader_desaparecer()

Abrir contrato
   ↓
aguardar_loader_desaparecer()

Abrir Arquivos
   ↓
aguardar_loader_desaparecer()

Trocar página
   ↓
aguardar_loader_desaparecer()
```

Evitar:

```python id="4cr3vn"
time.sleep(5)
```

quando for possível aguardar diretamente uma condição da interface.

---

# 13. Timeout do loader

A função de espera deverá possuir um limite.

A automação não poderá permanecer indefinidamente esperando o loader desaparecer.

Exemplo conceitual:

```text id="y3zgfi"
Loader apareceu
      ↓
Aguardar
      ↓
Desapareceu?
 │
 ├── SIM → continuar
 │
 └── NÃO
       ↓
    Timeout
       ↓
    Registrar erro
```

---

# 14. Pasta do projeto

Antes de iniciar os downloads, criar uma pasta correspondente ao projeto.

Estrutura:

```text id="v63wsf"
downloads/
└── <numero_projeto>/
```

Exemplo:

```text id="mczjcc"
downloads/
└── 12345/
```

Todos os documentos encontrados deverão ser armazenados nessa pasta.

Não importa se o contrato é:

```text id="0y5mmx"
ATIVO
ou
ENCERRADO
```

ambos utilizarão:

```text id="py4mza"
downloads/12345/
```

---

# 15. Criação da pasta

Criar uma função específica.

Exemplo:

```python id="8k4e3c"
def criar_pasta_projeto(numero_projeto):
    """
    Cria e retorna o diretório utilizado para armazenar
    os anexos do projeto informado.
    """
```

A função deverá:

1. Receber o projeto.
2. Determinar o diretório.
3. Criar a pasta caso não exista.
4. Aceitar uma pasta já existente.
5. Retornar o caminho utilizado.

---

# 16. Download dos anexos

Para cada documento encontrado:

```text id="t6ydfr"
Identificar anexo
      ↓
Solicitar download
      ↓
Aguardar conclusão
      ↓
Salvar na pasta do projeto
      ↓
Confirmar arquivo
      ↓
Registrar log
```

O simples clique no botão de download não deverá ser considerado, por si só, confirmação de que o arquivo foi salvo corretamente.

---

# 17. Arquivos com nomes repetidos

Contratos diferentes podem possuir anexos com nomes iguais.

Exemplo:

```text id="zdipsp"
Contrato 001
└── documento.pdf

Contrato 002
└── documento.pdf
```

A automação não deverá sobrescrever silenciosamente arquivos existentes.

Uma estratégia possível:

```text id="4ib8gd"
documento.pdf
documento_2.pdf
documento_3.pdf
```

A regra definitiva deverá preservar os documentos.

Caso futuramente seja necessário verificar se dois arquivos são realmente idênticos pelo conteúdo, essa responsabilidade deverá ser implementada separadamente.

---

# 18. Estrutura sugerida

```text id="ceigfk"
baixar-anexos-projetos-conveniar/
│
├── src/
│   ├── main.py
│   ├── config.py
│   ├── login.py
│   ├── contratos.py
│   ├── anexos.py
│   └── loader.py
│
├── tests/
│   ├── test_contratos.py
│   ├── test_anexos.py
│   └── test_loader.py
│
├── docs/
│   └── desenvolvimento.md
│
├── downloads/
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

A estrutura poderá evoluir durante o desenvolvimento.

Não criar módulos apenas para seguir uma estrutura previamente definida.

---

# 19. Responsabilidade dos módulos

## `main.py`

Responsável pela orquestração.

Exemplo conceitual:

```python id="tq54mj"
def main():
    projeto = obter_projeto()

    pasta = criar_pasta_projeto(projeto)

    fazer_login()

    abrir_busca_contratos()

    configurar_filtros(projeto)

    buscar_contratos()

    processar_resultados(pasta)
```

O `main.py` não deverá possuir todas as regras da automação.

---

## `login.py`

Responsável por:

```text id="fxw88g"
fazer login
validar login
```

Possíveis funções:

```python id="rvsyjz"
fazer_login()
validar_login()
```

---

## `contratos.py`

Responsável pela consulta e processamento dos resultados.

Possíveis funções:

```python id="as7ly8"
abrir_busca_contratos()

limpar_filtros_data()

selecionar_tipo_contrato()

selecionar_projeto()

buscar_contratos()

obter_linhas_resultado()

obter_situacao()

situacao_deve_ser_processada()

processar_contrato()

existe_proxima_pagina()

ir_para_proxima_pagina()
```

---

## `anexos.py`

Responsável pelos arquivos.

Possíveis funções:

```python id="32y4w6"
abrir_aba_arquivos()

obter_anexos()

baixar_anexo()

criar_pasta_projeto()

resolver_nome_arquivo()

confirmar_download()
```

---

## `loader.py`

Responsável pelo controle do carregamento.

Possível função:

```python id="d3b3a1"
aguardar_loader_desaparecer()
```

---

# 20. Separar regra de negócio da interface

Sempre que possível, regras simples deverão ficar separadas da automação do navegador.

Por exemplo, a decisão:

> "Esta situação deve ser processada?"

pode existir independentemente do navegador.

Exemplo:

```python id="iw55g6"
SITUACOES_PERMITIDAS = {
    "ATIVO",
    "ENCERRADO",
}


def situacao_deve_ser_processada(situacao):
    situacao = situacao.strip().upper()

    return situacao in SITUACOES_PERMITIDAS
```

Isso facilita:

* leitura;
* manutenção;
* testes;
* reutilização;
* investigação de erros.

---

# 21. Funções pequenas

Evitar uma única função responsável por:

```text id="as2fjg"
login
+
busca
+
filtros
+
paginação
+
situação
+
contrato
+
anexos
+
downloads
```

Preferir responsabilidades pequenas:

```python id="3cx0y1"
fazer_login()

configurar_filtros()

buscar_contratos()

obter_situacao()

situacao_deve_ser_processada()

processar_contrato()

baixar_anexos()
```

Uma função deverá possuir um objetivo claro.

---

# 22. Logs

Registrar acontecimentos relevantes.

Exemplo:

```text id="mp1zg1"
[INFO] Automação iniciada
[INFO] Projeto: 12345
[INFO] Pasta: downloads/12345

[INFO] Login realizado

[INFO] Consultando contratos
[INFO] Página 1

[INFO] Contrato 1001 - ATIVO
[INFO] Processando contrato 1001
[INFO] 3 anexos encontrados
[INFO] Download concluído: documento.pdf

[INFO] Contrato 1002 - CANCELADO
[DEBUG] Contrato ignorado

[INFO] Contrato 1003 - ENCERRADO
[INFO] Processando contrato 1003

[INFO] Página 2
...

[INFO] Automação finalizada
```

Nunca registrar credenciais.

---

# 23. Tratamento de erros

O desenvolvimento deverá priorizar primeiro o fluxo principal.

```text id="3rhz86"
login
→ consulta
→ resultados
→ situação
→ contrato
→ arquivos
→ anexos
→ download
```

Depois fortalecer os cenários de erro.

Considerar:

* falha no login;
* projeto inexistente;
* nenhum resultado;
* situação ausente;
* situação desconhecida;
* contrato sem anexos;
* falha ao abrir contrato;
* loader que não desaparece;
* timeout;
* erro de paginação;
* download não concluído;
* arquivo existente;
* mudança na interface;
* elemento não encontrado.

Evitar:

```python id="08ouau"
try:
    executar()
except:
    pass
```

Erros não deverão desaparecer silenciosamente.

---

# 24. Testes

As funções deverão ser construídas pensando em testabilidade.

Fluxo:

```text id="fphn0w"
Criar função
     ↓
Entender entrada
     ↓
Entender saída
     ↓
Criar cenário normal
     ↓
Criar casos de borda
     ↓
Executar testes
```

Nem todo clique no navegador precisa possuir um teste unitário.

Priorizar regras que podem ser isoladas.

---

# 25. Testes da situação

Esta passa a ser uma das regras mais importantes da automação.

Exemplos:

```python id="um67cj"
def test_ativo_deve_ser_processado():
    assert situacao_deve_ser_processada("ATIVO") is True


def test_encerrado_deve_ser_processado():
    assert situacao_deve_ser_processada("ENCERRADO") is True


def test_cancelado_nao_deve_ser_processado():
    assert situacao_deve_ser_processada("CANCELADO") is False
```

Também testar normalização:

```python id="nkslv1"
def test_situacao_deve_ignorar_maiusculas_minusculas():
    assert situacao_deve_ser_processada("Ativo") is True


def test_situacao_deve_ignorar_espacos():
    assert situacao_deve_ser_processada(" ENCERRADO ") is True
```

O estagiário poderá começar por esses testes porque possuem regra simples e resultado objetivo.

---

# 26. Testes de paginação

Considerar:

```text id="n7n05s"
uma página
várias páginas
última página
página sem contratos válidos
próxima página inexistente
```

É especialmente importante verificar que:

```text id="htfrvp"
Página sem ATIVO/ENCERRADO
```

não seja confundida com:

```text id="k8gj7e"
Fim da paginação
```

A automação deverá continuar para a próxima página mesmo quando nenhuma linha da página atual for processada.

---

# 27. Testes da pasta

Testar:

```text id="n55sw4"
pasta não existe
pasta já existe
caminho retornado
projeto válido
entrada inválida
```

---

# 28. Testes de arquivos

Testar:

```text id="ppnnzb"
arquivo normal
arquivo existente
nomes repetidos
extensão preservada
download concluído
falha de download
```

---

# 29. Testes do loader

Quando possível:

```text id="ajc57z"
loader não existe
loader aparece
loader desaparece
loader não desaparece
timeout
```

---

# 30. Orientação para o estagiário

O foco inicial do estagiário será:

* entender o fluxo;
* acompanhar execuções;
* entender as funções existentes;
* documentar funções;
* melhorar docstrings;
* criar testes;
* executar testes;
* identificar comportamentos inesperados;
* reproduzir erros;
* registrar problemas encontrados.

A correção de erros não será inicialmente a principal responsabilidade.

Ela poderá aumentar progressivamente conforme houver maior domínio do projeto.

---

# 31. Como analisar uma função

Antes de documentar ou testar:

```text id="1cj3e1"
1. O que esta função faz?

2. O que ela recebe?

3. O que ela retorna?

4. Ela modifica alguma coisa?

5. Quem chama essa função?

6. Qual é o comportamento esperado?

7. Quais entradas podem causar problemas?
```

Depois ler a implementação.

O objetivo é compreender a função antes de simplesmente escrever testes.

---

# 32. Docstrings

Funções importantes deverão possuir documentação.

Exemplo:

```python id="c9my53"
def situacao_deve_ser_processada(situacao):
    """
    Verifica se um contrato deve ser processado com base
    em sua situação.

    Args:
        situacao: Situação apresentada na linha do contrato.

    Returns:
        True para contratos ATIVO ou ENCERRADO.
        False para as demais situações.
    """
```

Outro exemplo:

```python id="53e3nf"
def criar_pasta_projeto(numero_projeto):
    """
    Cria o diretório utilizado para armazenar os anexos
    pertencentes ao projeto.

    Args:
        numero_projeto: Número identificador do projeto.

    Returns:
        Caminho do diretório criado ou existente.
    """
```

---

# 33. Comentários

Evitar:

```python id="t3rlax"
# Verifica se está ativo
if situacao == "ATIVO":
```

O código já explica isso.

Preferir comentários que expliquem decisões:

```python id="6us1qd"
# A consulta é realizada sem filtro de situação para evitar
# duas consultas e duas paginações independentes.
```

Comentários devem explicar principalmente **por que** uma decisão foi tomada.

---

# 34. Encontrando um erro

Quando um erro for encontrado:

```text id="zn2ntb"
Identificar
   ↓
Reproduzir
   ↓
Registrar cenário
   ↓
Identificar função
   ↓
Criar teste quando aplicável
   ↓
Corrigir
   ↓
Executar testes
```

Registrar:

```text id="n7md6i"
Erro:

Projeto:

Página:

Contrato:

Situação:

Etapa:

Comportamento esperado:

Comportamento obtido:

Como reproduzir:

Mensagem de erro:
```

---

# 35. Divisão inicial do trabalho

## Desenvolvimento principal

Responsável principalmente por:

* arquitetura;
* configuração do navegador;
* login;
* navegação;
* filtros;
* leitura da tabela;
* paginação;
* acesso aos contratos;
* download;
* controle do loader;
* tratamento dos principais erros;
* decisões técnicas.

## Estagiário

Responsável inicialmente por:

* compreender o projeto;
* acompanhar o fluxo;
* documentar funções;
* criar e melhorar docstrings;
* criar testes unitários;
* executar a suíte de testes;
* identificar erros;
* reproduzir problemas;
* documentar comportamentos inesperados.

Funções simples e isoladas, como a validação da situação, são boas candidatas para o início do trabalho do estagiário.

---

# 36. Git

Sugestões de branches:

```text id="iz0mb6"
feature/login

feature/filtros-contratos

feature/leitura-resultados

feature/paginacao

feature/download-anexos

feature/loader

test/situacao-contrato

test/download-anexos

docs/desenvolvimento
```

Exemplos de commits:

```text id="pwwsqh"
feat: adiciona login no sistema

feat: adiciona filtros da consulta

feat: adiciona leitura da situação dos contratos

feat: processa contratos ativos e encerrados

feat: implementa paginação

feat: adiciona download dos anexos

feat: cria diretório por projeto

test: adiciona testes de situação dos contratos

test: adiciona testes de arquivos duplicados

fix: evita sobrescrever anexos

docs: atualiza fluxo da automação
```

---

# 37. Pull Request

Antes de abrir um PR:

```text id="vbsxwi"
[ ] Código executado

[ ] Testes passando

[ ] Nova regra possui teste quando aplicável

[ ] Nenhuma credencial adicionada

[ ] Código revisado

[ ] Funções relevantes documentadas

[ ] README atualizado quando necessário

[ ] Código temporário/debug removido
```

O PR deverá informar:

```text id="7j7lvd"
O que foi feito?

Por que foi feito?

Como testar?

Existe alguma limitação conhecida?
```

---

# 38. Critérios de conclusão

A automação será considerada funcional quando conseguir:

* [ ] realizar login;
* [ ] validar o login;
* [ ] acessar a busca de contratos;
* [ ] selecionar **Contrato de Bolsas**;
* [ ] limpar os filtros de data;
* [ ] informar o projeto;
* [ ] realizar a consulta sem filtro de situação;
* [ ] identificar a situação de cada linha;
* [ ] processar contratos **ATIVO**;
* [ ] processar contratos **ENCERRADO**;
* [ ] ignorar outras situações;
* [ ] percorrer todas as páginas;
* [ ] continuar a paginação mesmo quando uma página não possuir contratos válidos;
* [ ] acessar cada contrato válido;
* [ ] acessar **Arquivos**;
* [ ] localizar **Anexos**;
* [ ] identificar todos os documentos;
* [ ] criar a pasta do projeto;
* [ ] baixar todos os anexos;
* [ ] salvar todos os documentos na pasta correta;
* [ ] evitar sobrescrever arquivos silenciosamente;
* [ ] confirmar downloads quando possível;
* [ ] aguardar corretamente os loaders;
* [ ] possuir timeout para carregamentos;
* [ ] continuar quando um contrato não possuir anexos;
* [ ] gerar logs úteis;
* [ ] tratar os principais erros;
* [ ] possuir testes das regras relevantes;
* [ ] possuir documentação suficiente para manutenção.

---

# 39. Regra de desenvolvimento

Priorizar:

```text id="jj0fv9"
Entender
   ↓
Implementar
   ↓
Fazer funcionar
   ↓
Testar
   ↓
Tratar erros
   ↓
Documentar
   ↓
Refatorar
```

Evitar complexidade desnecessária.

O objetivo não é apenas construir uma automação que funcione.

O projeto deverá permitir que outro integrante da equipe consiga:

```text id="wmuzer"
entender
   ↓
executar
   ↓
testar
   ↓
identificar erros
   ↓
corrigir
   ↓
continuar o desenvolvimento
```

sem depender exclusivamente do desenvolvedor que criou a automação.
