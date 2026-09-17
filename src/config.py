"""Configurações da automação."""

import os
import sys
from pathlib import Path


from dotenv import load_dotenv

BASE_DIR = (
    Path(sys.executable).resolve().parent
    if getattr(sys, "frozen", False)
    else Path(__file__).resolve().parent.parent
)



load_dotenv(BASE_DIR / ".env")

USUARIO = os.getenv("USUARIO")
SENHA = os.getenv("SENHA")
HEADLESS = os.getenv("HEADLESS", "true").strip().lower() == "true"
URL = os.getenv("URL")
