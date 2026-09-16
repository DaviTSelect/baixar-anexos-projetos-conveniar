"""Configurações da automação."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DOWNLOADS_DIR = BASE_DIR / "downloads"

load_dotenv(BASE_DIR / ".env")

USUARIO = os.getenv("USUARIO")
SENHA = os.getenv("SENHA")
HEADLESS = os.getenv("HEADLESS", "true").strip().lower() == "true"
URL = os.getenv("URL")