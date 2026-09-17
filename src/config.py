"""Configurações da automação."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def obter_diretorio_aplicacao():
    """
    Retorna o diretório onde estão os arquivos da aplicação.

    Em produção:
        usa a pasta onde está o executável (.exe).

    Em desenvolvimento:
        usa a raiz do projeto.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent.parent


BASE_DIR = obter_diretorio_aplicacao()

ENV_PATH = BASE_DIR / ".env"

load_dotenv(
    dotenv_path=ENV_PATH,
    override=False,
)


USUARIO = os.getenv("USUARIO")
SENHA = os.getenv("SENHA")
HEADLESS = os.getenv(
    "HEADLESS",
    "true",
).strip().lower() == "true"
URL = os.getenv("URL")