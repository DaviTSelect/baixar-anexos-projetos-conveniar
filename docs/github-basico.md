# Git e GitHub: primeiros passos

Git guarda o histórico do projeto no computador. GitHub hospeda uma cópia compartilhada e permite revisar alterações em equipe.

## Palavras que você vai encontrar

| Termo | Significado |
| --- | --- |
| Repositório | Pasta do projeto com seu histórico Git. |
| Branch | Linha de trabalho; permite desenvolver uma tarefa separadamente. |
| Stage ou índice | Seleção dos arquivos que entrarão no próximo commit. |
| Commit | Registro local das alterações selecionadas, com uma mensagem. |
| `origin` | Nome usado para o repositório remoto configurado. |
| Push | Envia commits locais para o remoto. |
| Fetch | Atualiza as referências do remoto sem integrar alterações nos seus arquivos. |
| Pull | Busca e integra alterações do remoto na branch atual. |
| Pull Request (PR) | Pedido para revisar e integrar uma branch em outra no GitHub. |
| Merge | Integra o histórico de uma branch em outra. |
| Conflito | Alterações que o Git precisa que alguém concilie. |

## Preparar o computador

No terminal, confira o Git e configure sua identidade uma vez, substituindo os exemplos pelos seus dados:

```powershell
git --version
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@example.com"
```

Esses dados identificam os commits; não fazem login no GitHub. Use o e-mail aprovado pela equipe ou o endereço de privacidade disponibilizado pela sua conta. A opção `--global` vale para seus repositórios nesse computador.

Se ainda não tem o projeto, obtenha a URL com a equipe e use `git clone URL_DO_REPOSITORIO`. Se a pasta já existe, abra-a no editor e use o terminal nela, sem clonar novamente.

## Rotina de trabalho

1. Confira `git status` e `git branch --show-current`.
2. Combine a branch de origem com a equipe. Com o diretório sem alterações pendentes, troque para ela e atualize-a.
3. Crie uma branch para sua tarefa, faça as alterações e valide o resultado.
4. Revise os arquivos e envie pelo [atalho de envio](../ferramentas/github/README.md).
5. Abra um PR e aguarde a revisão da equipe.

Exemplo **se a equipe indicar `dev` como base** e essa branch já existir localmente:

```powershell
git switch dev
git pull --ff-only origin dev
git switch -c docs/exemplos-interface
```

`--ff-only` recusa a integração se os históricos divergirem. Se falhar, pare e peça ajuda; não apague alterações para contornar o problema. Nunca presuma que `dev` é a base correta de toda tarefa.

## Conferir e enviar manualmente

```powershell
git status
git diff
git add docs/componentes-interface.md
git diff --cached
git commit -m "docs: explica componentes da interface"
git push -u origin docs/exemplos-interface
```

Adapte o arquivo e a branch ao seu trabalho. `git diff` mostra alterações ainda não preparadas; `git diff --cached` mostra o conteúdo selecionado para o commit. Arquivos novos ainda não adicionados devem ser revisados no editor.

O push acima publica a branch indicada e configura seu acompanhamento com `-u`. Commit salva localmente; push envia ao remoto. Consulte a [referência oficial de git push](https://git-scm.com/docs/git-push).

Mensagens úteis descrevem uma mudança concreta:

- `feat: adiciona campo de projeto`
- `fix: corrige validação do projeto vazio`
- `docs: explica execução da interface`
- `test: cobre situação de contrato inválida`

Evite mensagens como `alterações`, `teste` ou `arrumei`.

## Abrir um Pull Request

No GitHub, abra o repositório e a área **Pull requests**, inicie um novo PR e confira a branch de destino (`base`) e a sua branch (`compare`). Preencha o [modelo do projeto](../.github/PULL_REQUEST_TEMPLATE.md) com o que mudou e como validou. Use PR em rascunho se o trabalho ainda não estiver pronto para revisão.

Push não faz merge. Aguarde a revisão e a orientação da equipe antes de integrar. Quando pedirem ajustes, faça novos commits na mesma branch e envie novamente; eles passam a fazer parte do PR. Consulte a [documentação de criação de PRs](https://docs.github.com/pt/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request).

## Comandos de consulta

| Comando | Para que serve |
| --- | --- |
| `git status` | Ver arquivos alterados e o estado da branch. |
| `git branch --show-current` | Ver a branch atual. |
| `git branch -a` | Listar branches locais e referências remotas conhecidas. |
| `git log --oneline -5` | Ver os cinco commits mais recentes. |
| `git remote -v` | Conferir os destinos remotos. |
| `git fetch origin` | Atualizar as referências do remoto. |

## Cuidados no projeto

Não envie `.env`, senhas, downloads ou arquivos temporários. O `.gitignore` não deixa de rastrear um arquivo que já foi adicionado anteriormente. Não use `git add -f` para forçar a inclusão de arquivos ignorados.

Se encontrar conflito ou push rejeitado, guarde a mensagem e peça ajuda. Não use `git push --force`, `git reset --hard` ou exclusão de arquivos como tentativa de resolver um erro. Consulte as [regras do repositório](../AGENTS.md).

O projeto ainda tem limitações descritas no [guia de desenvolvimento](desenvolvimento.md). Informe no PR o que conseguiu validar; não marque a automação completa como testada apenas porque uma janela abriu.
