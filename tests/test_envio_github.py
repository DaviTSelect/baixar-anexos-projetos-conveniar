"""Integração do script Windows com Git e remoto local, sem acessar o GitHub."""

from pathlib import Path
import shutil
import subprocess

import pytest


pytestmark = pytest.mark.skipif(
    not shutil.which("powershell.exe") or not shutil.which("git"),
    reason="Requer PowerShell do Windows e Git",
)


def git(pasta, *args):
    return subprocess.run(
        ["git", "-C", str(pasta), *args], check=True,
        capture_output=True, text=True, encoding="utf-8",
    ).stdout.strip()


@pytest.fixture
def repositorio(tmp_path):
    local = tmp_path / "projeto com espacos"
    remoto = tmp_path / "remoto.git"
    local.mkdir()
    git(tmp_path, "init", "--bare", str(remoto))
    git(local, "init", "-b", "feature/teste")
    git(local, "config", "user.name", "Teste")
    git(local, "config", "user.email", "teste@example.com")
    git(local, "config", "commit.gpgsign", "false")
    git(local, "config", "core.hooksPath", str(tmp_path / "sem-hooks"))
    git(local, "remote", "add", "origin", str(remoto))
    pasta = local / "ferramentas" / "github"
    pasta.mkdir(parents=True)
    origem = Path(__file__).resolve().parents[1] / "ferramentas" / "github" / "enviar.ps1"
    shutil.copy2(origem, pasta)
    (local / ".gitignore").write_text(".env\n", encoding="utf-8")
    git(local, "add", ".")
    git(local, "commit", "-m", "inicio")
    return local, remoto


def enviar(local, respostas):
    return subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
         str(local / "ferramentas" / "github" / "enviar.ps1")],
        input=respostas, capture_output=True, text=True, timeout=30,
    )


def test_commit_envio_branch_atual_e_reenvio(repositorio):
    local, remoto = repositorio
    mensagem = 'docs: exemplo $HOME; & literal'
    (local / "exemplo.txt").write_text("teste", encoding="utf-8")
    (local / ".env").write_text("FICTICIO=teste", encoding="utf-8")
    resultado = enviar(local, mensagem + "\nSIM\n")
    assert resultado.returncode == 0, resultado.stdout + resultado.stderr
    assert git(local, "log", "-1", "--format=%s") == mensagem
    assert git(local, "rev-parse", "HEAD") == git(remoto, "rev-parse", "refs/heads/feature/teste")
    assert git(local, "rev-parse", "--abbrev-ref", "@{upstream}") == "origin/feature/teste"
    assert ".env" not in git(remoto, "ls-tree", "--name-only", "feature/teste").splitlines()
    anterior = git(local, "rev-parse", "HEAD")
    assert enviar(local, "SIM\n").returncode == 0
    assert git(local, "rev-parse", "HEAD") == anterior


@pytest.mark.parametrize("respostas,codigo", [("\n", 1), ("docs: teste\nNAO\n", 0)])
def test_cancelamento_preserva_indice(repositorio, respostas, codigo):
    local, remoto = repositorio
    (local / "novo.txt").write_text("teste", encoding="utf-8")
    anterior = git(local, "rev-parse", "HEAD")
    estado = git(local, "status", "--porcelain")
    assert enviar(local, respostas).returncode == codigo
    assert git(local, "rev-parse", "HEAD") == anterior
    assert git(local, "status", "--porcelain") == estado
    assert git(remoto, "for-each-ref") == ""


def test_bloqueia_env_rastreado(repositorio):
    local, remoto = repositorio
    (local / ".env").write_text("FICTICIO=teste", encoding="utf-8")
    git(local, "add", "-f", ".env")
    resultado = enviar(local, "docs: teste\nSIM\n")
    assert resultado.returncode == 1
    assert 'Um arquivo .env seria versionado' in resultado.stdout
    assert git(remoto, "for-each-ref") == ""


def test_sem_branch_ativa(repositorio):
    local, remoto = repositorio
    git(local, "checkout", "--detach")
    resultado = enviar(local, "SIM\n")
    assert resultado.returncode == 1
    assert "detached HEAD" in resultado.stdout
    assert git(remoto, "for-each-ref") == ""


def test_push_rejeitado_preserva_commit(repositorio, tmp_path):
    local, remoto = repositorio
    git(local, "push", "-u", "origin", "feature/teste")
    outro = tmp_path / "outro"
    git(tmp_path, "clone", "--branch", "feature/teste", str(remoto), str(outro))
    git(outro, "config", "user.name", "Teste")
    git(outro, "config", "user.email", "teste@example.com")
    git(outro, "config", "commit.gpgsign", "false")
    git(outro, "config", "core.hooksPath", str(tmp_path / "sem-hooks"))
    (outro / "outro.txt").write_text("outro", encoding="utf-8")
    git(outro, "add", ".")
    git(outro, "commit", "-m", "outro commit")
    git(outro, "push", "origin", "feature/teste")
    remoto_antes = git(remoto, "rev-parse", "feature/teste")
    (local / "local.txt").write_text("local", encoding="utf-8")
    resultado = enviar(local, "docs: commit local\nSIM\n")
    assert resultado.returncode == 1
    assert git(local, "log", "-1", "--format=%s") == "docs: commit local"
    assert git(remoto, "rev-parse", "feature/teste") == remoto_antes
