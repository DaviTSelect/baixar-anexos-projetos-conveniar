# Versionamento e padrão de commits

Este documento define a convenção para mensagens de commit e a orientação para versões e releases do projeto. Para os comandos do dia a dia, consulte o [guia básico de Git e GitHub](github-basico.md).

O projeto está em desenvolvimento. Os números apresentados aqui são **exemplos**, não a versão atual. O script de envio não calcula versões nem publica releases automaticamente.

## 1. Commit, versão, tag e release

| Termo | Significado |
| --- | --- |
| Commit | Registro de alterações no histórico local do Git. |
| Versão | Número que identifica um conjunto de alterações disponibilizado pela equipe. |
| Tag | Referência que identifica um commit específico, por exemplo `v2.3.0`. |
| Release no GitHub | Publicação associada a uma tag, com notas da versão e, quando necessário, arquivos para distribuição. |

Vários commits podem fazer parte da mesma versão. Criar um commit ou enviar uma branch não exige criar uma versão a cada vez.

## 2. Versionamento semântico

A convenção adotada neste documento é o formato `MAJOR.MINOR.PATCH`. Para aplicá-la, a equipe precisa definir o que constitui a interface pública e a compatibilidade do sistema: funções usadas por integrações, configurações aceitas e comportamentos documentados. Consulte a [especificação SemVer](https://semver.org/lang/pt-BR/).

```text
2.2.2
│ │ │
│ │ └── PATCH: correção compatível
│ └──── MINOR: funcionalidade nova compatível
└────── MAJOR: mudança incompatível
```

Para versões estáveis, a partir de `1.0.0`:

| Componente | Quando incrementar | Exemplo |
| --- | --- | --- |
| PATCH | Corrigir um comportamento incorreto mantendo compatibilidade. | `2.2.2 → 2.2.3` |
| MINOR | Adicionar funcionalidade compatível ou declarar uma funcionalidade pública obsoleta. | `2.2.2 → 2.3.0` |
| MAJOR | Introduzir uma mudança incompatível na interface pública. | `2.2.2 → 3.0.0` |

Ao incrementar MINOR, PATCH volta a zero. Ao incrementar MAJOR, MINOR e PATCH voltam a zero. A versão deve refletir a mudança de maior impacto entre as incluídas no lançamento.

Durante o desenvolvimento inicial, SemVer usa `0.y.z`, sem prometer uma interface estável. A equipe deve definir a versão inicial e o momento de publicar `1.0.0`; este guia não declara que o projeto já atingiu essa fase.

## 3. Exemplos para este projeto

| Alteração hipotética | Classificação para uma versão estável |
| --- | --- |
| Corrigir o caminho do ChromeDriver sem mudar a configuração exigida. | PATCH |
| Adicionar uma configuração opcional preservando o comportamento anterior. | MINOR |
| Remover uma configuração pública ainda usada pelas integrações. | MAJOR |
| Tornar obrigatório um parâmetro antes opcional de uma função pública. | MAJOR |
| Corrigir um erro de digitação no README. | Não exige incremento automático. |
| Reorganizar código interno ou adicionar testes sem mudar comportamento. | Avaliar no conjunto da release; não exige incremento automático. |

O tamanho da alteração não determina a versão: uma mudança de uma linha pode quebrar compatibilidade. Documentação, testes e manutenção não devem ser classificados automaticamente como PATCH.

## 4. Padrão de mensagens de commit

Use uma descrição curta, em português, que explique a alteração. O formato segue [Conventional Commits](https://www.conventionalcommits.org/pt-br/v1.0.0/):

```text
tipo: descrição
```

Um escopo opcional identifica a área afetada:

```text
fix(browser): corrige inicialização do ChromeDriver
```

| Tipo | Quando usar | Exemplo |
| --- | --- | --- |
| `feat` | Nova funcionalidade. | `feat: adiciona consulta por projeto` |
| `fix` | Correção de bug. | `fix: corrige caminho do ChromeDriver` |
| `docs` | Alteração somente de documentação. | `docs: explica componentes de interface` |
| `refactor` | Reorganização interna sem adicionar funcionalidade nem corrigir bug. | `refactor: reorganiza configuração do navegador` |
| `test` | Inclusão ou alteração de testes. | `test: cobre cancelamento do envio` |
| `chore` | Manutenção do projeto. | `chore: atualiza dependências de desenvolvimento` |

Escolha o tipo pelo efeito da alteração. Uma atualização de dependência que corrige um bug ou quebra compatibilidade precisa comunicar esse impacto. Evite mensagens vagas como `ajustes`, `teste` ou `arrumei`.

## 5. Mudanças incompatíveis

Use `!` depois do tipo ou escopo para indicar quebra de compatibilidade. Explique o que mudou e como adaptar o uso; o rodapé `BREAKING CHANGE:` também sinaliza a incompatibilidade.

Exemplo hipotético de mensagem completa:

```text
refactor(browser)!: exige novo parâmetro na consulta

BREAKING CHANGE: buscar_contratos passa a exigir o parâmetro exemplo.
As integrações devem informar esse parâmetro em cada chamada.
```

Esse exemplo não descreve uma alteração já implementada. Qualquer tipo de commit pode conter uma mudança incompatível, inclusive `fix` e `refactor`.

O prefixo ajuda a organizar o histórico, mas não executa uma publicação. Não há automação de release definida neste repositório que transforme essas mensagens em novas versões.

## 6. Enviar o trabalho para revisão

```text
Alteração → Validação → Commit → Push da branch → Pull Request → Revisão → Merge
```

O [atalho de envio](../ferramentas/github/README.md) pede uma mensagem, mostra a branch atual e solicita confirmação antes de criar o commit e fazer push. Ele inclui todas as alterações não ignoradas e as já preparadas no índice. Confira a lista antes de confirmar.

O atalho não troca de branch, abre PR, faz merge ou cria tags e releases. Para mensagens com corpo e rodapé, como o exemplo anterior, prepare o commit manualmente com `git commit`, usando o editor configurado. Depois, com o diretório sem novas alterações, o atalho pode enviar os commits existentes.

Não envie credenciais ou `.env`. Siga as [regras do repositório](../AGENTS.md) e registre as verificações realizadas no [modelo de PR](../.github/PULL_REQUEST_TEMPLATE.md).

## 7. Preparar uma versão

Quando a equipe decidir publicar uma versão:

1. Confirme que as alterações previstas foram revisadas e integradas.
2. Identifique a branch e o commit aprovados para a publicação.
3. Execute as verificações pertinentes e registre limitações conhecidas.
4. Defina o número da versão considerando todas as alterações desde a versão anterior.
5. Prepare notas com funcionalidades, correções e instruções de migração, se houver.
6. Crie e envie a tag aprovada; depois publique a release no GitHub.

A publicação deve ser solicitada pelo responsável, conforme o `AGENTS.md`. Os exemplos abaixo são orientações e não autorizam executar uma release.

## 8. Criar a tag e publicar a release

Primeiro, confira o estado do repositório, o commit atual e as tags locais:

```powershell
git status
git branch --show-current
git log -1 --oneline
git tag --list
```

Esses comandos não confirmam quais tags existem apenas no remoto. Antes de publicar, confira também o GitHub e o destino `origin` com a equipe.

**Somente com o commit correto em `HEAD`, o diretório sem alterações pendentes e a versão aprovada**, o exemplo para `2.3.0` seria:

```powershell
git tag -a v2.3.0 -m "Release 2.3.0"
git push origin refs/tags/v2.3.0
```

A tag aponta para o commit, não para alterações ainda sem commit. O prefixo `v` é uma convenção do nome da tag; o número da versão é `2.3.0`.

Enviar a tag não cria, por si só, uma release no GitHub. Na área **Releases** do repositório, crie uma publicação associada à tag enviada e preencha as notas. Não mova ou sobrescreva uma tag de versão publicada para incluir correções: prepare uma nova versão.

Para o uso diário, o estagiário deve seguir o fluxo de branch, commit, push e PR; a preparação da release acontece quando a equipe definir um lançamento.
