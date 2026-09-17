"""Gera o executável em dist com o ícone e os recursos da interface."""

from importlib.util import find_spec
from pathlib import Path
import subprocess
import sys


def main():
    if sys.platform != "win32":
        raise SystemExit("Execute este script no Windows para gerar o .exe.")

    raiz = Path(__file__).resolve().parent
    for modulo in ("PyInstaller", "customtkinter", "selenium", "dotenv"):
        if find_spec(modulo) is None:
            raise SystemExit(
                "Dependências ausentes. Execute: "
                "python -m pip install -r requirements-build.txt"
            )

    icone = raiz / "icon" / "logo.ico"
    if not icone.is_file():
        raise SystemExit(f"Ícone não encontrado: {icone}")

    # O spec gerado fica em build/ para preservar o main.spec existente.
    subprocess.run(
        [
            sys.executable, "-m", "PyInstaller",
            "--noconfirm", "--clean", "--onefile", "--windowed",
            "--name", "Anexos - Contratos por Projeto",
            "--distpath", str(raiz / "dist"),
            "--workpath", str(raiz / "build" / "pyinstaller"),
            "--specpath", str(raiz / "build"),
            "--paths", str(raiz / "src"),
            "--icon", str(icone),
            "--add-data", f"{icone};icon",
            "--collect-data", "customtkinter",
            # O Selenium carrega o driver do Chrome dinamicamente.
            "--hidden-import", "selenium.webdriver.chrome.webdriver",
            "--hidden-import", "selenium.webdriver.chrome.options",
            "--collect-data", "selenium",
            str(raiz / "src" / "main.py"),
        ],
        cwd=raiz,
        check=True,
    )
    print(f"Executável criado: {raiz / 'dist' / 'Anexos - Contratos por Projeto.exe'}")
    print("Configure o .env ao lado do executável antes de usar a automação.")


if __name__ == "__main__":
    main()
