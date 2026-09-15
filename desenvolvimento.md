# Guia de Desenvolvimento

Este documento contém as orientações técnicas para desenvolvimento, testes e manutenção da automação de download de anexos dos contratos de bolsistas por projeto.

O objetivo é permitir que qualquer integrante da equipe consiga entender o fluxo da automação, desenvolver novas funcionalidades, criar testes e investigar erros.

---

# 1. Fluxo geral

A automação deverá executar o seguinte processo:

```text
Login
  ↓
Acessar busca de contratos
  ↓
Selecionar "Contrato de Bolsas"
  ↓
Limpar filtros de data
  ↓
Informar projeto
  ↓
Buscar contratos ATIVOS
  ↓
Percorrer todas as páginas
  ↓
Buscar contratos ENCERRADOS
  ↓
Percorrer todas as páginas
  ↓
Abrir cada contrato
  ↓
Acessar Arquivos
  ↓
Localizar Anexos
  ↓
Baixar todos os documentos
  ↓
Salvar na pasta do projeto
```

---

# 2. Regra principal de desenvolvimento

O desenvolvimento deverá seguir esta ordem:

```text
Entender o problema
       ↓
Criar função
       ↓
Fazer funcionar
       ↓
Testar
       ↓
Tratar erros relevantes
       ↓
Documentar
       ↓
Refatorar quando necessário
```

Evitar criar abstrações ou estruturas complexas antes de existir uma necessidade real.

Priorizar código:

* simples;
* legível;
* testável;
* dividido por responsabilidade;
* fácil de investigar quando ocorrer um erro.

---

# 3. Estrutura sugerida

```text
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
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

A estrutura poderá mudar conforme o projeto evoluir.

Não criar arquivos apenas para seguir essa estrutura. Um novo módulo deve existir quando houver uma responsabilidade clara para ele.

---

# 4. Responsabilidades

## `main.py`

Responsável por coordenar a execução.

Exemplo conceitual:

```python
def main():
    projeto = obter_projeto()

    pasta = criar_pasta_projeto(projeto)

    fazer_login()

    abrir_busca_contratos()

    processar_status(
        projeto=projeto,
        status="ATIVO",
        pasta_destino=pasta,
    )

    processar_status(
        projeto=projeto,
        status="ENCERRADO",
        pasta_destino=pasta,
    )
```

O `main.py` não deve concentrar todas as regras da automação.

---

## `login.py`

Responsável pelo processo de autenticação.

Possíveis responsabilidades:

```python
fazer_login()
validar_login()
```

Credenciais não deverão estar diretamente no código.

Utilizar variáveis de ambiente.

Nunca registrar senha nos logs.

---

## `contratos.py`

Responsável pela consulta e navegação relacionada aos contratos.

Possíveis funções:

```python
abrir_busca_contratos()

limpar_filtros_data()

selecionar_tipo_contrato()

selecionar_projeto()

selecionar_status()

buscar_contratos()

obter_contratos_da_pagina()

existe_proxima_pagina()

ir_para_proxima_pagina()

abrir_contrato()
```

A paginação deve ser considerada obrigatória.

Nunca assumir que todos os contratos estarão na primeira página.

---

## `anexos.py`

Responsável pela identificação e download dos documentos.

Possíveis funções:

```python
abrir_aba_arquivos()

obter_anexos()

baixar_anexo()

criar_pasta_projeto()

resolver_nome_arquivo()
```

Todos os anexos deverão ser armazenados na pasta correspondente ao projeto.

Exemplo:

```text
downloads/
└── 12345/
    ├── documento.pdf
    ├── termo.pdf
    └── comprovante.pdf
```

---

## `loader.py`

Responsável exclusivamente pelo controle dos indicadores de carregamento da interface.

Deverá existir uma função central:

```python
def aguardar_loader_desaparecer(page):
    """
    Aguarda até que o loader da aplicação deixe de bloquear
    a interação com a página.
    """
```

Essa função deverá ser reutilizada em toda a automação.

---

# 5. Regra do loader

Este é um requisito importante do projeto.

Sempre que uma ação puder provocar carregamento:

```text
executar ação
     ↓
aguardar loader desaparecer
     ↓
continuar
```

Exemplo conceitual:

```python
clicar_buscar()

aguardar_loader_desaparecer(page)

obter_resultados()
```

Evitar:

```python
time.sleep(5)
```

Uma espera fixa não garante que a aplicação terminou de carregar.

Em uma execução o sistema pode levar 1 segundo e em outra pode levar 8 segundos.

A automação deverá, sempre que possível, aguardar uma condição real da interface.

---

# 6. Consulta dos contratos

Para cada projeto deverão ser realizadas duas consultas:

```text
ATIVO
ENCERRADO
```

O fluxo esperado é:

```python
for status in ("ATIVO", "ENCERRADO"):
    selecionar_status(status)

    buscar_contratos()

    processar_resultados()
```

Essa estrutura é apenas conceitual. A implementação poderá ser diferente.

---

# 7. Paginação

Depois de realizar a consulta:

```text
Página atual
     ↓
Obter contratos
     ↓
Processar contratos
     ↓
Existe próxima página?
     │
     ├── SIM → próxima página
     │
     └── NÃO → finalizar status
```

É importante evitar:

* processar a mesma página duas vezes;
* ignorar a última página;
* entrar em loop infinito;
* perder contratos ao retornar da página de detalhes.

A estratégia de navegação deverá ser documentada quando for implementada.

---

# 8. Processamento de contrato

Cada contrato deverá seguir aproximadamente:

```text
Abrir contrato
      ↓
Aguardar loader
      ↓
Abrir Arquivos
      ↓
Aguardar loader
      ↓
Localizar Anexos
      ↓
Obter lista de documentos
      ↓
Baixar documentos
      ↓
Confirmar downloads
      ↓
Retornar
```

Um contrato sem anexos não deverá interromper o processamento dos demais.

---

# 9. Organização dos downloads

Antes de processar os contratos, criar o diretório:

```text
downloads/<projeto>/
```

Exemplo:

```text
downloads/12345/
```

Todos os contratos ativos e encerrados do projeto utilizarão o mesmo diretório.

---

# 10. Arquivos duplicados

Nunca sobrescrever silenciosamente um arquivo.

Pode acontecer:

```text
Contrato A → documento.pdf
Contrato B → documento.pdf
```

Mas os conteúdos podem ser diferentes.

Uma estratégia inicial poderá gerar:

```text
documento.pdf
documento_2.pdf
documento_3.pdf
```

Posteriormente, caso seja necessário identificar duplicidade pelo conteúdo, essa regra deverá ser implementada separadamente e coberta por testes.

---

# 11. Funções pequenas

Evitar funções muito grandes.

Ruim:

```python
def executar_automacao():
    # login
    # filtros
    # busca
    # paginação
    # contratos
    # downloads
    # erros
    # ...
```

Preferir responsabilidades separadas:

```python
fazer_login()

configurar_filtros()

buscar_contratos()

processar_contrato()

baixar_anexos()
```

Uma função deve ter um objetivo fácil de explicar.

Se for difícil explicar o que uma função faz em uma frase, provavelmente ela está fazendo coisas demais.

---

# 12. Tratamento de erros

Não esconder erros.

Evitar:

```python
try:
    executar()
except:
    pass
```

Quando um erro ocorrer, precisamos conseguir responder:

```text
O que falhou?
Onde falhou?
Qual projeto estava sendo processado?
Qual contrato estava sendo processado?
Qual operação estava sendo executada?
```

Quando possível, registrar essas informações.

Não incluir informações sensíveis nos logs.

---

# 13. Logs

Exemplo de execução:

```text
[INFO] Iniciando automação
[INFO] Projeto: 12345

[INFO] Realizando login
[INFO] Login realizado

[INFO] Buscando contratos ATIVOS
[INFO] Página 1
[INFO] 10 contratos encontrados

[INFO] Contrato 1/10
[INFO] 4 anexos encontrados
[INFO] Download concluído: documento.pdf

[INFO] Contrato 2/10
[WARNING] Nenhum anexo encontrado

[INFO] Página 2
...

[INFO] Buscando contratos ENCERRADOS
...

[INFO] Automação finalizada
```

Logs devem ajudar na investigação de problemas.

---

# 14. Como criar testes

Antes de escrever um teste, responda:

```text
O que esta função faz?

O que ela recebe?

O que ela retorna?

O que deve acontecer normalmente?

O que pode dar errado?
```

Depois crie os cenários.

Exemplo:

```python
def criar_pasta_projeto(projeto):
    ...
```

Pensamento para os testes:

```text
Projeto válido
    ↓
pasta deve ser criada

Pasta já existe
    ↓
função deve continuar funcionando

Projeto inválido
    ↓
qual comportamento esperamos?
```

Só depois escrever o teste.

---

# 15. O que testar

Priorizar funções que possuem lógica própria.

### Pasta do projeto

Testar:

```text
criação
pasta existente
caminho retornado
entrada inválida
```

### Arquivos

Testar:

```text
nome normal
nome duplicado
extensão
arquivo existente
```

### Contratos

Quando a lógica estiver separada da interface:

```text
lista vazia
um contrato
vários contratos
dados incompletos
contratos duplicados
```

### Paginação

Testar quando possível:

```text
uma página
várias páginas
última página
ausência de próxima página
```

### Loader

Testar:

```text
loader desaparece
loader já não existe
timeout
```

---

# 16. Testes de navegador

Nem tudo precisa ser teste unitário.

Uma função como:

```python
calcular_nome_arquivo()
```

é excelente para teste unitário.

Já:

```text
clicar no botão Arquivos
```

depende do navegador e da página.

Nesse caso podem ser utilizados:

* mocks;
* fixtures;
* testes de integração;
* testes controlados utilizando o próprio sistema.

O objetivo não é alcançar cobertura artificial criando testes sem valor.

---

# 17. Orientação para o estagiário

Antes de alterar qualquer função:

1. Leia a função completa.
2. Leia sua docstring.
3. Veja onde ela é utilizada.
4. Veja os testes existentes.
5. Execute os testes.
6. Entenda entrada e saída.
7. Só então faça alterações.

Se não entender uma função, pergunte antes de modificar.

---

# 18. Documentação de funções

Funções relevantes deverão possuir docstrings.

Exemplo:

```python
def criar_pasta_projeto(numero_projeto):
    """
    Cria o diretório utilizado para armazenar os anexos de um projeto.

    Args:
        numero_projeto: Número identificador do projeto.

    Returns:
        Caminho do diretório criado ou já existente.
    """
```

Não documentar apenas por obrigação.

A documentação deve ajudar outro desenvolvedor a entender como utilizar a função.

---

# 19. Comentários

Comentários devem explicar principalmente **por quê**.

Evitar:

```python
# Clica no botão
botao.click()
```

Preferir:

```python
# O resultado só fica disponível depois que o loader global desaparece.
aguardar_loader_desaparecer(page)
```

O código já mostra o que está acontecendo.

O comentário deve explicar decisões que não são evidentes.

---

# 20. Encontrando um erro

Quando encontrar um erro, não começar imediatamente alterando várias partes do código.

Registrar:

```text
Erro:
Etapa:
Projeto:
Contrato:
Comportamento esperado:
Comportamento obtido:
Mensagem apresentada:
Como reproduzir:
```

Depois tente reproduzir o problema.

Se o erro puder ser representado por um teste:

```text
erro encontrado
      ↓
criar teste que reproduz
      ↓
teste falha
      ↓
corrigir código
      ↓
teste passa
```

Essa é uma das práticas mais importantes para aprender durante este projeto.

---

# 21. Git

Cada alteração deve possuir objetivo claro.

Exemplos de branches:

```text
feature/login
feature/filtros-contratos
feature/paginacao
feature/download-anexos
feature/loader
test/download-anexos
docs/desenvolvimento
```

Exemplos de commits:

```text
feat: adiciona login no sistema

feat: adiciona filtro de contratos de bolsas

feat: implementa paginação dos contratos

feat: adiciona download dos anexos

test: adiciona testes de criação da pasta do projeto

fix: evita sobrescrever anexos com mesmo nome

docs: documenta fluxo de desenvolvimento
```

Evitar commits genéricos como:

```text
alterações
teste
correção
update
```

---

# 22. Pull Request

Antes de abrir um PR:

```text
[ ] Código executado localmente
[ ] Testes passando
[ ] Nova lógica possui testes quando aplicável
[ ] Nenhuma credencial adicionada
[ ] Código revisado
[ ] Funções novas documentadas
[ ] README/docs atualizados quando necessário
[ ] Sem arquivos temporários
[ ] Sem código de debug desnecessário
```

O PR deve explicar:

```text
O que foi feito?
Por que foi feito?
Como testar?
Existe alguma limitação conhecida?
```

---

# 23. Definição de pronto

Uma funcionalidade pode ser considerada concluída quando:

```text
funciona
+
é compreensível
+
possui tratamento básico de erros
+
possui testes quando aplicável
+
está documentada
```

O objetivo deste projeto não é apenas criar uma automação que funcione hoje.

O código deverá ser compreensível o suficiente para que outro integrante da equipe consiga testar, investigar erros e continuar o desenvolvimento no futuro.
