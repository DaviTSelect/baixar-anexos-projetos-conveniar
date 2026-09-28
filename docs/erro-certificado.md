# Erro de certificado ao verificar atualizações

## O que aconteceu

Ao abrir o executável e verificar atualizações, foi apresentada a mensagem:

```text
certificate verify failed: unable to get local issuer certificate (_ssl.c:1010)
```

Essa etapa consulta o GitHub por HTTPS, usando `urlopen` em [src/update.py](../src/update.py). O erro ocorreu durante o uso do aplicativo, e não durante a geração pelo [criar_executavel.py](../criar_executavel.py).

HTTPS usa certificados para verificar a identidade do servidor. O Python precisa ligar o certificado apresentado a uma autoridade certificadora (CA) confiável, por meio de uma cadeia de certificados. A mensagem indica que não foi possível completar essa cadeia com os certificados disponíveis na conexão e no ambiente.

O trecho `_ssl.c:1010` identifica um ponto da implementação interna de SSL do Python; não é uma linha do código deste projeto.

## Por que pode ocorrer

Antes da correção, as requisições dependiam dos certificados encontrados pelo contexto padrão do Python. Uma CA pública ausente no ambiente pode impedir a validação. Outra possibilidade é a inspeção HTTPS por proxy ou antivírus corporativo, que apresenta certificados assinados pela autoridade da organização. Uma cadeia incompleta enviada pelo servidor ou por um intermediário também pode produzir esse erro.

A causa específica na máquina onde ocorreu o problema ainda não foi confirmada. A mensagem, sozinha, não prova que o certificado do GitHub seja inválido nem que o PyInstaller tenha causado a falha. O fato de a página abrir no navegador também não garante que o Python esteja usando as mesmas fontes de confiança.

## Correção aplicada no projeto

O aplicativo agora cria um contexto TLS seguro, carrega os certificados confiáveis do sistema e acrescenta os certificados públicos do `certifi`. Esse contexto é usado tanto na consulta de releases quanto no download de atualizações.

O pacote foi declarado em [requirements.txt](../requirements.txt), e o script de geração inclui seus dados no executável. A validação do certificado e do nome do servidor permanece habilitada.

O `certifi` fornece uma coleção de autoridades certificadoras públicas. Ele não inclui automaticamente a CA privada de uma organização. Consulte a [documentação do certifi](https://github.com/certifi/python-certifi) e a [documentação de SSL do Python](https://docs.python.org/3.12/library/ssl.html) para os mecanismos utilizados.

## Como aplicar manualmente em uma cópia antiga

Os passos abaixo já estão implementados nesta cópia do projeto. Ao trabalhar em outra cópia, confira o código antes de adicionar imports ou funções para evitar duplicação. Execute os comandos na raiz do projeto, no ambiente Python usado para gerar o executável.

### 1. Instalar e declarar a dependência

```powershell
python -m pip install --upgrade certifi
```

Acrescente uma linha `certifi` ao `requirements.txt`, se ainda não existir.

### 2. Criar o contexto TLS

Em `src/update.py`, acrescente os imports e a função:

```python
import ssl
import certifi


def _contexto_ssl():
    contexto = ssl.create_default_context()
    contexto.load_verify_locations(cafile=certifi.where())
    return contexto
```

`create_default_context()` carrega a confiança padrão do sistema e habilita as verificações de segurança. `load_verify_locations()` acrescenta as CAs do `certifi` ao contexto.

### 3. Usar o contexto nas duas requisições

Na chamada de `urlopen` de `verificar_atualizacoes()`, acrescente `context=_contexto_ssl()`, preservando o processamento existente da resposta:

```python
with urlopen(
    requisicao,
    timeout=15,
    context=_contexto_ssl(),
) as resposta:
    release = json.load(resposta)
```

Faça a mesma inclusão na chamada de `urlopen` de `baixar_atualizacao()`, mantendo seu timeout de `60` segundos e o restante da rotina de download.

### 4. Incluir os certificados no empacotamento

Em `criar_executavel.py`, acrescente `certifi` à sequência de módulos verificados por `find_spec`. Na lista de argumentos passada ao PyInstaller, inclua:

```python
"--collect-data", "certifi",
```

Isso inclui o arquivo de certificados do pacote no executável.

### 5. Gerar e usar o novo executável

Feche o aplicativo antes de recompilar. O comando de geração substitui o executável de mesmo nome em `dist/`.

```powershell
python -m pip install -r requirements-build.txt
python criar_executavel.py
```

Abra `dist/Anexos - Contratos por Projeto.exe` e verifique as atualizações. Mantenha a configuração local `.env` ao lado do executável, conforme o [README](../README.md), sem incorporá-la ao pacote.

Instalar `certifi` no computador ou editar o código-fonte não altera um executável já gerado. É necessário recompilar e usar o novo arquivo.

## O que foi verificado

Na implementação da correção, os quatro testes de [tests/test_update_ssl.py](../tests/test_update_ssl.py) passaram. Eles verificam a preservação das CAs do sistema, a inclusão das CAs do pacote, o uso de TLS verificado nas duas requisições e a ausência de nova tentativa sem validação após um erro de certificado.

Para executar esses testes isolados:

```powershell
python -B -m unittest discover -s tests -p test_update_ssl.py
```

O registro da implementação anterior informa geração do executável e confirmação de `certifi/cacert.pem` em seu conteúdo. A revisão atual de testes e documentação não recompilou nem inspecionou esse executável. Os testes usam respostas simuladas e diretórios temporários; não comprovam acesso real ao GitHub na rede afetada. Essa confirmação ainda está pendente.

Os testes de `tests/test_update.py` foram alinhados ao retorno atual de três valores e ao fluxo obrigatório. Consulte a [matriz de testes e pendências](testes.md). Uma falha de certificado mantém o painel bloqueado até uma verificação bem-sucedida.

## Se o erro persistir

Confirme primeiro que está abrindo o executável recém-gerado. Se a rede utiliza inspeção HTTPS, solicite à equipe de TI a verificação da cadeia apresentada e da instalação da CA corporativa confiável no Windows. O pacote de CAs públicas não resolve sozinho esse caso.

Não desative a validação SSL como correção: isso eliminaria a verificação da identidade do servidor. Para investigar, registre a mensagem completa, a etapa da falha e qual executável foi usado, sem incluir credenciais ou o conteúdo do `.env`.
