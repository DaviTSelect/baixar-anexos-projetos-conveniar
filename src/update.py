"""Verificação e download das atualizações pelo GitHub."""

import json
import os
import re
import tempfile

from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


VERSAO_ATUAL = "1.1.1"

REPOSITORIO = "DaviTSelect/baixar-anexos-projetos-conveniar"

RELEASES_URL = (
    f"https://github.com/{REPOSITORIO}/releases/latest"
)

API_URL = (
    f"https://api.github.com/repos/{REPOSITORIO}/releases/latest"
)


STATUS_ATUALIZADO = "atualizado"
STATUS_DISPONIVEL = "disponivel"
STATUS_ERRO = "erro"


def numero_versao(valor):
    """Converte 1.2.3 ou v1.2.3 em tupla numérica."""

    if not isinstance(valor, str):
        raise ValueError("Versão inválida")

    resultado = re.fullmatch(
        r"v?(0|[1-9][0-9]*)\."
        r"(0|[1-9][0-9]*)\."
        r"(0|[1-9][0-9]*)",
        valor,
    )

    if resultado is None:
        raise ValueError(f"Versão inválida: {valor}")

    return tuple(
        int(parte)
        for parte in resultado.groups()
    )


def _requisicao(
    url,
    accept="application/vnd.github+json",
):
    """Cria uma requisição HTTP para o GitHub."""

    return Request(
        url,
        headers={
            "Accept": accept,
            "User-Agent": "Anexos-Conveniar",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )


def verificar_atualizacoes():
    """
    Verifica a última release estável no GitHub.

    Retorna:
        mensagem, status, url_download

    status pode ser:
        STATUS_ATUALIZADO
        STATUS_DISPONIVEL
        STATUS_ERRO
    """

    try:
        requisicao = _requisicao(API_URL)

        with urlopen(
            requisicao,
            timeout=15,
        ) as resposta:
            release = json.load(resposta)

        if not isinstance(release, dict):
            raise ValueError(
                "Resposta inválida do GitHub"
            )

        if release.get("draft"):
            return (
                "A última release encontrada é um rascunho.",
                STATUS_ERRO,
                None,
            )

        if release.get("prerelease"):
            return (
                "A última release encontrada é uma pré-release.",
                STATUS_ERRO,
                None,
            )

        versao = release.get("tag_name")

        if not versao:
            return (
                "A release não possui uma versão válida.",
                STATUS_ERRO,
                None,
            )

        versao_remota = numero_versao(versao)
        versao_local = numero_versao(VERSAO_ATUAL)

        # Mesma versão ou versão local superior.
        if versao_remota <= versao_local:
            return (
                f"Versão {VERSAO_ATUAL} já está atualizada.",
                STATUS_ATUALIZADO,
                None,
            )

        assets = release.get("assets", [])

        if not isinstance(assets, list):
            return (
                "A lista de arquivos da release é inválida.",
                STATUS_ERRO,
                None,
            )

        instalador = None

        for asset in assets:

            if not isinstance(asset, dict):
                continue

            nome = str(
                asset.get("name", "")
            )

            if nome.lower().endswith(".exe"):
                instalador = asset
                break

        if instalador is None:
            return (
                (
                    f"Nova versão {versao} encontrada, "
                    "mas o instalador .exe ainda não "
                    "foi publicado."
                ),
                STATUS_ERRO,
                None,
            )

        url_download = instalador.get(
            "browser_download_url"
        )

        if not url_download:
            return (
                (
                    "Não foi possível encontrar a URL "
                    "do instalador."
                ),
                STATUS_ERRO,
                None,
            )

        return (
            f"Nova versão {versao} encontrada.",
            STATUS_DISPONIVEL,
            url_download,
        )

    except HTTPError as erro:

        if erro.code == 404:
            return (
                "Não foi possível encontrar a release.",
                STATUS_ERRO,
                None,
            )

        return (
            (
                "Erro ao consultar o GitHub "
                f"(HTTP {erro.code})."
            ),
            STATUS_ERRO,
            None,
        )

    except (URLError, OSError) as erro:

        return (
            (
                "Não foi possível conectar ao GitHub: "
                f"{erro}"
            ),
            STATUS_ERRO,
            None,
        )

    except (ValueError, TypeError) as erro:

        return (
            (
                "Não foi possível verificar "
                f"atualizações: {erro}"
            ),
            STATUS_ERRO,
            None,
        )


def baixar_atualizacao(
    url_download,
    progresso=None,
):
    """
    Baixa o instalador da atualização.

    progresso(percentual, baixados, total)
    """

    if not url_download:
        raise ValueError(
            "URL de download não informada"
        )

    nome = (
        url_download
        .rstrip("/")
        .split("/")[-1]
    )

    nome = re.sub(
        r"[^A-Za-z0-9_.-]",
        "_",
        nome,
    )

    if not nome.lower().endswith(".exe"):
        nome += ".exe"

    caminho = os.path.join(
        tempfile.gettempdir(),
        nome,
    )

    requisicao = _requisicao(
        url_download,
        accept="application/octet-stream",
    )

    try:

        with urlopen(
            requisicao,
            timeout=60,
        ) as resposta:

            total = resposta.headers.get(
                "Content-Length"
            )

            try:
                total = (
                    int(total)
                    if total
                    else 0
                )

            except (TypeError, ValueError):
                total = 0

            baixados = 0

            with open(
                caminho,
                "wb",
            ) as arquivo:

                while True:

                    bloco = resposta.read(
                        1024 * 1024
                    )

                    if not bloco:
                        break

                    arquivo.write(bloco)

                    baixados += len(bloco)

                    if progresso:

                        if total:
                            percentual = int(
                                baixados
                                * 100
                                / total
                            )
                        else:
                            percentual = -1

                        progresso(
                            percentual,
                            baixados,
                            total,
                        )

    except Exception:

        # Remove download incompleto.
        try:
            if os.path.exists(caminho):
                os.remove(caminho)
        except OSError:
            pass

        raise

    if not os.path.exists(caminho):
        raise OSError(
            "O arquivo de atualização não foi criado."
        )

    tamanho = os.path.getsize(caminho)

    if tamanho == 0:

        try:
            os.remove(caminho)
        except OSError:
            pass

        raise OSError(
            "O arquivo de atualização está vazio."
        )

    return caminho