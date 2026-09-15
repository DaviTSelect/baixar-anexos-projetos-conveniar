"""Ponto de entrada da automação."""

from pathlib import Path

from config import DOWNLOADS_DIR


def criar_pasta_projeto(numero_projeto: str) -> Path:
    """Cria e retorna a pasta de downloads do projeto."""
    numero = str(numero_projeto).strip()

    if not numero:
        raise ValueError("Número do projeto não informado.")

    pasta = DOWNLOADS_DIR / numero
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def main():
    """Executa a automação.

    O fluxo do navegador será implementado progressivamente.
    """
    print("Automação ainda em desenvolvimento.")


if __name__ == "__main__":
    main()
