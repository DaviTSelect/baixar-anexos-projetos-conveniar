import tkinter as tk
from tkinter import messagebox
import shutil
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
import time
from dotenv import load_dotenv
from pathlib import Path
from config import DOWNLOADS_DIR,URL,USUARIO,SENHA,HEADLESS
from selenium.webdriver.chrome.service import Service


def realizar_login():
    

    DOWNLOADS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Configura Chrome
    options = webdriver.ChromeOptions()

    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": str(DOWNLOADS_DIR),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
    )
    #
    
    user_profile = os.environ["USERPROFILE"]

    chromedriver_path = os.path.join(
        user_profile,
        "Chrome",
        "chromedriver.exe"
    )

    chrome_path = os.path.join(
        user_profile,
        "Chrome",
        "GoogleChrome",
        "App",
        "Chrome-bin",
        "chrome.exe"
    )


    # Verifica se o ChromeDriver existe
    if not os.path.isfile(chromedriver_path):
        root = tk.Tk()
        root.withdraw()

        messagebox.showerror(
            "Arquivo não encontrado",
            f"O ChromeDriver não foi encontrado.\n\n"
            f"Caminho esperado:\n{chromedriver_path}"
        )

        root.destroy()
        raise SystemExit


    # Verifica se o Chrome existe
    if not os.path.isfile(chrome_path):
        root = tk.Tk()
        root.withdraw()

        messagebox.showerror(
            "Arquivo não encontrado",
            f"O Google Chrome não foi encontrado.\n\n"
            f"Caminho esperado:\n{chrome_path}"
        )

        root.destroy()
        raise SystemExit


    # Se encontrou os dois, inicia o Selenium
    service = Service(
        executable_path=chromedriver_path
    )

    
    options.binary_location = chrome_path

    

    if HEADLESS:
        options.add_argument("--headless=new")
   
    driver = webdriver.Chrome(
        options=options,service=service
    )
    
    
    #LOGIN
    
    wait = WebDriverWait(driver,30)
    driver.get(URL)
    
    usuario_login = wait.until(
        EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_ObjWucLoginCaptcha_lgUsuario_UserName"))
    )
    usuario_login.send_keys(USUARIO)
    aguardar_loader_desaparecer(driver)
    print("Usuario inserido!")

    senha_login = wait.until(
            EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_ObjWucLoginCaptcha_lgUsuario_Password"))
        )
    senha_login.send_keys(SENHA)
    aguardar_loader_desaparecer(driver)
    print("Senha inserida!")
    entrar_login = wait.until(
                EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_ObjWucLoginCaptcha_lgUsuario_btnLogin"))
            )
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        entrar_login
    )

    driver.execute_script(
        "arguments[0].click();",
        entrar_login
    )
    aguardar_loader_desaparecer(driver)
    print("Logado com sucesso!")
   
    print("-"*50)
    
    return driver

def buscar_contratos(driver,numero_projeto):
    wait = WebDriverWait(driver,30)
    #funcao de selecionar tipo de contrato
    abrir_lista_tipo = wait.until(
                EC.element_to_be_clickable((By.ID, "input_dropdown_upctl00_ContentPlaceHolder1_UpTipoContrato"))
            )
    abrir_lista_tipo.click()
    contrato_bolsa = driver.find_element(
        By.XPATH,
        "//table[@id='table_itens']//span[normalize-space()='Contrato de Bolsa']"
    )

    contrato_bolsa.click()
    print("Selecionado tipo: Contrato de Bolsa")
    aguardar_loader_desaparecer(driver)
    
    #funcao de inserir nome do projeto
    projeto =  wait.until(EC.element_to_be_clickable((By.ID, "input_autocompletectl00_ContentPlaceHolder1_UpConvenio")))
    projeto.click()
    projeto.send_keys(numero_projeto)
    aguardar_loader_desaparecer(driver)

    projeto = driver.find_element(
        By.XPATH,
        f"//table[@id='table_itens']//span[contains(normalize-space(), '{numero_projeto} -')]"
    )

    projeto.click()
    aguardar_loader_desaparecer(driver)
    #funcao de limpeza de data
    data_inicio = wait.until(
                    EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_txtDataInicial"))
                )
    data_inicio.clear()
    aguardar_loader_desaparecer(driver)
    #funcao de buscar
    btn_consultar = wait.until(
                        EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_btnConsultar"))
                    )
    btn_consultar.click()
    aguardar_loader_desaparecer(driver)

    driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);"
    )
    aguardar_loader_desaparecer(driver)
    driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);"
    )
    aguardar_loader_desaparecer(driver)
    driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);"
    )
    aguardar_loader_desaparecer(driver)
    linhas = driver.find_elements(
    By.XPATH,
    "//tr[contains(@class, 'gridRow') or contains(@class, 'gridAlternateRow')]"
    )

    resultados = []

    for linha in linhas:

        colunas = linha.find_elements(By.TAG_NAME, "td")

        if len(colunas) < 11:
            continue

        coluna_link = colunas[1]
        coluna_projeto = colunas[2]
        coluna_status = colunas[10]

        projeto = coluna_projeto.text.strip()
        status = coluna_status.text.strip()

        # Verifica o número do projeto
        if not projeto.startswith(f"{numero_projeto} -"):
            continue

        # Verifica se está Ativo ou Encerrado
        if status.lower() not in ("ativo", "encerrado"):
            continue

        # Procura o link do contrato
        links = coluna_link.find_elements(By.TAG_NAME, "a")

        if not links:
            continue

        resultados.append({
            "contrato": coluna_link.text.strip(),
            "projeto": projeto,
            "status": status,
            "link": links[0]
        })

    return resultados

    
    #contrato = {href,projeto,tipo,situacao}
    

def processar_contrato(driver, item, projeto):

    contrato = item["contrato"]

    # Pasta downloads
    BASE_DIR = Path(__file__).resolve().parent.parent
    PASTA_DOWNLOAD = BASE_DIR / "downloads"

    # downloads/377/1250_2026
    pasta_destino = (
        PASTA_DOWNLOAD
        / str(projeto)
        / contrato.replace("/", "_")
    )

    pasta_destino.mkdir(
        parents=True,
        exist_ok=True
    )

    print(f"Pasta destino: {pasta_destino}")

    # Guarda página anterior
    pagina_anterior = driver.current_window_handle

    # Abre contrato
    link = item["link"]

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        link
    )
    aguardar_loader_desaparecer(driver)
    time.sleep(0.5)

    driver.execute_script(
        "arguments[0].click();",
        link
    )
    
    time.sleep(2)
    aguardar_loader_desaparecer(driver)
    # Vai para última janela
    driver.switch_to.window(
        driver.window_handles[-1]
    )
    aguardar_loader_desaparecer(driver)
    # Clica em Arquivos
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'a[href="#tabArquivo"]')
        )
    ).click()
    aguardar_loader_desaparecer(driver)
    # Tabela de anexos
    tabela = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.ID,
            "ctl00_ContentPlaceHolder1_ConvenioContratoArquivosUserControl1_gvwArquivoContrato"
        ))
    )

    # gridRow e gridAlternateRow
    linhas = tabela.find_elements(
        By.XPATH,
        ".//tr[contains(@class, 'gridRow') "
        "or contains(@class, 'gridAlternateRow')]"
    )

    downloads = []

    # Guarda IDs dos botões
    for linha in linhas:

        botoes = linha.find_elements(
            By.CSS_SELECTOR,
            'a[title="Baixar arquivo"]'
        )

        if botoes:
            downloads.append(
                botoes[0].get_attribute("id")
            )

    print(f"Arquivos para baixar: {len(downloads)}")

    # baixar  todos anexos 
    for botao_id in downloads:

        # Arquivos existentes ANTES deste download
        arquivos_antes = {
            arquivo
            for arquivo in PASTA_DOWNLOAD.iterdir()
            if arquivo.is_file()
        }

        # Localiza botão novamente
        botao = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.ID,
                botao_id
            ))
        )

        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            botao
        )
        aguardar_loader_desaparecer(driver)
        driver.execute_script(
            "arguments[0].click();",
            botao
        )
        aguardar_loader_desaparecer(driver)
        print(f"Baixando: {botao_id}")

        # espera aparecer um novo arquivo dentro da pasta download

        arquivo_baixado = None

        for _ in range(120):

            arquivos_agora = {
                arquivo
                for arquivo in PASTA_DOWNLOAD.iterdir()
                if arquivo.is_file()
            }

            novos = arquivos_agora - arquivos_antes

            # Ignora .crdownload
            completos = [
                arquivo
                for arquivo in novos
                if arquivo.suffix.lower() != ".crdownload"
            ]

            if completos:
                arquivo_baixado = completos[0]
                break

            time.sleep(1)

        # Se não apareceu, para a automação
        if arquivo_baixado is None:
            raise TimeoutError(
                f"Download não concluído: {botao_id}"
            )

       # move para pasta de destino 
        destino = pasta_destino / arquivo_baixado.name

        # Evita sobrescrever arquivo existente
        if destino.exists():
            print(f"Arquivo já existe: {destino.name}")

            # Remove o download duplicado
            arquivo_baixado.unlink()

        else:
            shutil.move(
                str(arquivo_baixado),
                str(destino)
            )

            print(f"Movido: {destino}")

        # Somente AGORA vai para o próximo
        print("Download confirmado!")
        print("-" * 50)

    # Fecha contrato
    driver.close()
    
    # Volta para página anterior
    driver.switch_to.window(pagina_anterior)

    print("Retornado para página anterior!")


    
def aguardar_loader_desaparecer(page, timeout=30):
    """Aguarda o loader desaparecer antes de continuar.

    Implemente o seletor real do loader quando a interface for mapeada.
    """
    raise NotImplementedError(
        "Defina o seletor do loader e a estratégia de espera do navegador."
    )
