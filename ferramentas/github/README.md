# Enviar sua branch para o GitHub

Use esta pasta para salvar suas alterações em um commit e enviar a branch atual para `origin`. Leia também o [guia básico de Git e GitHub](../../docs/github-basico.md).

## Como usar no Windows

1. Salve os arquivos no editor e confira se as alterações pertencem à sua tarefa.
2. Dê dois cliques em `enviar.cmd` ou execute `.\ferramentas\github\enviar.cmd` no terminal da raiz do projeto.
3. Confira a branch e a lista de arquivos exibidas. **Todos os arquivos alterados, novos e excluídos que não estejam ignorados serão incluídos**, além dos que já estavam preparados no Git.
4. Digite uma mensagem, como `docs: adiciona exemplos de interface`.
5. Digite `SIM` para criar o commit e enviar. Qualquer outra resposta cancela antes de preparar os arquivos.

O script identifica a branch a cada execução. Se você estiver em `dev`, o envio equivale a `git push -u origin dev`; em `feature-config`, envia `feature-config`. Ele não troca de branch. A opção `-u` configura o acompanhamento da branch remota. Veja a [documentação de git push](https://git-scm.com/docs/git-push).

Sem alterações, ele oferece enviar os commits já existentes, sem pedir nova mensagem. O push envia os commits locais ainda ausentes no remoto, incluindo commits anteriores ao criado pelo script.

## Antes da primeira execução

- Tenha o Git instalado e disponível no terminal: `git --version`.
- Configure seu nome e e-mail conforme o guia básico.
- Confira `git remote -v`: `origin` deve apontar para o repositório correto da equipe. O script usa esse destino já configurado.
- Tenha acesso ao repositório e autenticação pelo Git configurada. Se necessário, siga o login solicitado pelo gerenciador de credenciais; o script não armazena senhas.

O `.cmd` usa `ExecutionPolicy Bypass` somente no processo PowerShell que executa este script; não altera a política permanente do computador. Se uma política da organização bloquear a execução, peça orientação à equipe.

## Se houver erro

| Mensagem ou situação | Como proceder |
| --- | --- |
| Branch incorreta | Cancele e confira `git status` antes de trocar de branch. |
| Arquivo `.env` seria versionado | Peça ajuda para retirar o arquivo do índice e ajustar o `.gitignore`. Não envie credenciais. |
| Falta nome ou e-mail | Configure sua identidade e execute novamente. |
| `origin` não existe | Peça à equipe a URL correta antes de configurá-lo. |
| Permissão negada ou falha de autenticação | Confira sua conta e o acesso ao repositório. |
| Push rejeitado por histórico diferente | Não use `--force`. Consulte o guia e peça ajuda se houver divergência. |
| Falha de conexão depois do commit | O commit permanece local; execute novamente quando a conexão voltar. |

O script para ao encontrar uma falha; não faz pull, merge ou resolução automática de conflitos. Uma falha após `git add` pode deixar arquivos preparados para commit. Confira `git status` antes de tentar novamente.

Ele bloqueia arquivos chamados `.env` e `.env.*`, exceto `.env.example`, mas isso não detecta segredos em outros arquivos ou no histórico. Revise o conteúdo antes do envio. Não use esta ferramenta para selecionar apenas parte das alterações: nesse caso, siga os comandos manuais do guia.
