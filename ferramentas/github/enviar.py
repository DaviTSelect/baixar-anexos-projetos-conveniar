"""Cria um commit e envia a branch atual para origin após confirmação."""

from pathlib import Path
import shutil
import subprocess


def git(raiz, *argumentos, capturar=True):
    resultado = subprocess.run(
        ['git', *argumentos], cwd=raiz, capture_output=capturar,
        text=True, encoding='utf-8', errors='replace',
    )
    if resultado.returncode:
        if capturar and resultado.stderr:
            print(resultado.stderr.rstrip())
        raise RuntimeError(f'Git falhou: git {argumentos[0]}. Leia a mensagem acima.')
    return resultado.stdout if capturar else ''


def main():
    try:
        if not shutil.which('git'):
            raise RuntimeError('Instale o Git e abra o terminal novamente.')
        raiz = Path(__file__).resolve().parents[2]
        raiz_git = Path(git(raiz, 'rev-parse', '--show-toplevel').strip()).resolve()
        if raiz_git != raiz:
            raise RuntimeError('Mantenha este script em ferramentas/github dentro do repositorio.')
        branch = git(raiz, 'branch', '--show-current').strip()
        if not branch:
            raise RuntimeError('Voce esta sem branch ativa (detached HEAD). Selecione uma branch primeiro.')
        git(raiz, 'remote', 'get-url', '--push', 'origin')
        for marcador in ('MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-merge', 'rebase-apply'):
            caminho = Path(git(raiz, 'rev-parse', '--git-path', marcador).strip())
            if not caminho.is_absolute():
                caminho = raiz / caminho
            if caminho.exists():
                raise RuntimeError('Existe uma operacao Git em andamento. Conclua-a com ajuda da equipe antes de enviar.')

        # NUL preserva nomes com espaços, aspas e quebras de linha.
        arquivos = git(raiz, 'ls-files', '-z', '--cached', '--others', '--exclude-standard')
        for arquivo in arquivos.split('\0'):
            nome = arquivo.rsplit('/', 1)[-1].lower()
            if nome == '.env' or (nome.startswith('.env.') and nome != '.env.example'):
                raise RuntimeError('Um arquivo .env seria versionado. Remova-o da selecao do Git e ajuste o .gitignore com a equipe.')

        print(f'Branch atual: {branch}')
        print('Destino: origin (a mesma branch). Confira o destino com git remote -v.')
        estado = git(raiz, 'status', '--short')
        if estado.strip():
            print('Todos os arquivos abaixo, incluindo exclusoes, entrarao no commit:')
            print(estado.rstrip())
            print('Revise o conteudo com git diff e git diff --cached antes de continuar.')
            mensagem = input('Mensagem de commit (ex.: docs: explica componentes da interface): ')
            if not mensagem.strip():
                raise RuntimeError('Mensagem vazia. Nada foi adicionado ou enviado.')
        else:
            print('Sem alteracoes para novo commit. Os commits locais existentes serao enviados.')

        confirmacao = input(f"Confirmar envio da branch '{branch}' para origin? Digite SIM: ")
        if confirmacao != 'SIM':
            print('Cancelado. Nenhum commit ou push foi realizado.')
            return 0
        if estado.strip():
            git(raiz, 'add', '--all', capturar=False)
            git(raiz, 'commit', '-m', mensagem, capturar=False)
        git(raiz, 'push', '-u', 'origin', f'refs/heads/{branch}:refs/heads/{branch}', capturar=False)
        print(f'Envio concluido: {branch}. Abra um Pull Request no GitHub quando estiver pronto.')
        return 0
    except (RuntimeError, OSError, EOFError, KeyboardInterrupt) as erro:
        print(f'Falha: {erro or "Entrada interrompida."}')
        print('Se o commit ja foi criado, ele continua salvo localmente. Confira git status e git log -1.')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
