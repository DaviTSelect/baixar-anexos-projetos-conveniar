# Execute pelo enviar.cmd ou pelo PowerShell. Nao usa force push.
$ErrorActionPreference = 'Stop'
$codigoSaida = 0
$mudouDiretorio = $false

function Invoke-Git {
    param([string[]]$GitArgs)
    & git @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Git falhou: git $($GitArgs[0]). Leia a mensagem acima."
    }
}

try {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw 'Instale o Git e abra o terminal novamente.'
    }
    $raizEsperada = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
    Push-Location -LiteralPath $raizEsperada
    $mudouDiretorio = $true
    $raizGit = Invoke-Git -GitArgs @('rev-parse', '--show-toplevel')
    if ((Resolve-Path -LiteralPath $raizGit).Path -ne $raizEsperada) {
        throw 'Mantenha este script em ferramentas/github dentro do repositorio.'
    }
    $branch = Invoke-Git -GitArgs @('branch', '--show-current')
    if ([string]::IsNullOrWhiteSpace($branch)) {
        throw 'Voce esta sem branch ativa (detached HEAD). Selecione uma branch primeiro.'
    }
    $null = Invoke-Git -GitArgs @('remote', 'get-url', '--push', 'origin')
    foreach ($marcador in @('MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'rebase-merge', 'rebase-apply')) {
        $caminho = Invoke-Git -GitArgs @('rev-parse', '--git-path', $marcador)
        if (Test-Path -LiteralPath $caminho) {
            throw 'Existe uma operacao Git em andamento. Conclua-a com ajuda da equipe antes de enviar.'
        }
    }
    # .gitignore nao protege arquivos que ja foram adicionados ao Git.
    $arquivos = @(Invoke-Git -GitArgs @('ls-files', '--cached', '--others', '--exclude-standard'))
    $envIncluido = @($arquivos | Where-Object {
        $nome = ($_ -split '/')[-1]
        $nome -eq '.env' -or ($nome -like '.env.*' -and $nome -ne '.env.example')
    })
    if ($envIncluido.Count -gt 0) {
        throw 'Um arquivo .env seria versionado. Remova-o da selecao do Git e ajuste o .gitignore com a equipe.'
    }
    Write-Host "Branch atual: $branch"
    Write-Host 'Destino: origin (a mesma branch). Confira o destino com git remote -v.'
    $estado = @(Invoke-Git -GitArgs @('status', '--short'))
    if ($estado.Count -gt 0) {
        Write-Host 'Todos os arquivos abaixo, incluindo exclusoes, entrarao no commit:'
        $estado | ForEach-Object { Write-Host $_ }
        Write-Host 'Revise o conteudo com git diff e git diff --cached antes de continuar.'
        $mensagem = Read-Host 'Mensagem de commit (ex.: docs: explica componentes da interface)'
        if ([string]::IsNullOrWhiteSpace($mensagem)) {
            throw 'Mensagem vazia. Nada foi adicionado ou enviado.'
        }
    } else {
        Write-Host 'Sem alteracoes para novo commit. Os commits locais existentes serao enviados.'
    }
    $confirmacao = Read-Host "Confirmar envio da branch '$branch' para origin? Digite SIM"
    if ($confirmacao -cne 'SIM') {
        Write-Host 'Cancelado. Nenhum commit ou push foi realizado.'
    } else {
        if ($estado.Count -gt 0) {
            Invoke-Git -GitArgs @('add', '--all')
            Invoke-Git -GitArgs @('commit', '-m', $mensagem)
        }
        # Ref explicita evita ambiguidade com uma tag de mesmo nome.
        Invoke-Git -GitArgs @('push', '-u', 'origin', "refs/heads/${branch}:refs/heads/${branch}")
        Write-Host "Envio concluido: $branch. Abra um Pull Request no GitHub quando estiver pronto."
    }
} catch {
    Write-Host "Falha: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host 'Se o commit ja foi criado, ele continua salvo localmente. Confira git status e git log -1.'
    $codigoSaida = 1
} finally {
    if ($mudouDiretorio) { Pop-Location }
}
exit $codigoSaida
