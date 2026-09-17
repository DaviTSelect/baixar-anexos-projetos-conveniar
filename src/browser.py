import shutil
import os
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
import time
from dotenv import load_dotenv
from pathlib import Path
from config import URL,USUARIO,SENHA,HEADLESS
from selenium.webdriver.chrome.service import Service



def realizar_login(diretorio_destino=None):
    """Usa as credenciais fixas configuradas no .env via config.py."""

    if diretorio_destino is None:
        from config import BASE_DIR
        diretorio_destino = BASE_DIR / "downloads"

    diretorio_destino.mkdir(
        parents=True,
        exist_ok=True
    )

    # ============================================================
    # CONFIGURAÇÃO DO CHROME PORTÁTIL
    # ============================================================

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
        raise FileNotFoundError("ChromeDriver não encontrado no caminho configurado.")

    # Verifica se o Chrome existe
    if not os.path.isfile(chrome_path):
        raise FileNotFoundError("Google Chrome não encontrado no caminho configurado.")

    # ============================================================
    # CONFIGURAÇÃO DO SELENIUM
    # ============================================================

    options = webdriver.ChromeOptions()

    # Usa exatamente o Chrome portátil informado acima
    options.binary_location = chrome_path

    # Configurações de download
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": str(diretorio_destino),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
    )

    # Headless, caso esteja habilitado
    if HEADLESS:
        options.add_argument("--headless=new")

    # ============================================================
    # INICIA O CHROMEDRIVER MANUAL
    # ============================================================

    service = Service(
        executable_path=chromedriver_path
    )

    driver = webdriver.Chrome(
        service=service,
        options=options
    )

    # ============================================================
    # LOGIN
    # ============================================================

    try:
        wait = WebDriverWait(driver, 30)

        driver.get(URL)

        usuario_login = wait.until(
            EC.element_to_be_clickable(
                (
                    By.ID,
                    "ctl00_ContentPlaceHolder1_ObjWucLoginCaptcha_lgUsuario_UserName"
                )
            )
        )

        usuario_login.send_keys(USUARIO)
        aguardar_loader_desaparecer(driver)
        print("Usuario inserido!")

        senha_login = wait.until(
            EC.element_to_be_clickable(
                (
                    By.ID,
                    "ctl00_ContentPlaceHolder1_ObjWucLoginCaptcha_lgUsuario_Password"
                )
            )
        )

        senha_login.send_keys(SENHA)
        aguardar_loader_desaparecer(driver)
        print("Senha inserida!")

        entrar_login = wait.until(
            EC.element_to_be_clickable(
                (
                    By.ID,
                    "ctl00_ContentPlaceHolder1_ObjWucLoginCaptcha_lgUsuario_btnLogin"
                )
            )
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
        print("-" * 50)

    except BaseException:
        try:
            driver.quit()
        finally:
            raise

    return driver
def carregar_linhas_contratos(driver, timeout=30):
    """Rola até o fim e relê as linhas até estabilizarem por dois segundos."""
    seletor = "//tr[contains(@class, 'gridRow') or contains(@class, 'gridAlternateRow')]"
    assinatura_anterior = None
    estavel_desde = None

    def linhas_estaveis(navegador):
        nonlocal assinatura_anterior, estavel_desde
        estado = navegador.execute_script("""
            const pagina = document.scrollingElement || document.documentElement;
            window.scrollTo(0, pagina.scrollHeight);
            return {
                carregada: document.readyState === 'complete',
                altura: pagina.scrollHeight,
                noFinal: pagina.scrollTop + pagina.clientHeight >= pagina.scrollHeight - 1
            };
        """)
        if not (estado['carregada'] and estado['noFinal'] and
                EC.invisibility_of_element_located((By.ID, 'imgLoad'))(navegador)):
            assinatura_anterior = None
            estavel_desde = None
            return False

        try:
            # Relocaliza os elementos: o carregamento pode substituir as linhas.
            linhas = navegador.find_elements(By.XPATH, seletor)
            assinatura = (estado['altura'], tuple((linha.id, linha.text) for linha in linhas))
        except StaleElementReferenceException:
            assinatura_anterior = None
            estavel_desde = None
            return False

        agora = time.monotonic()
        if assinatura != assinatura_anterior:
            assinatura_anterior = assinatura
            estavel_desde = agora
        if agora - estavel_desde >= 2:
            # A tupla permite retornar também uma tabela vazia estabilizada.
            return (linhas,)
        return False

    return WebDriverWait(driver, timeout).until(
        linhas_estaveis,
        message='As linhas dos contratos não estabilizaram no final da página.',
    )[0]


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

    linhas = carregar_linhas_contratos(driver)

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
    

def processar_contrato(driver, item, projeto,diretorio_destino):

    contrato = item["contrato"]

    # Pasta downloads
    BASE_DIR = Path(__file__).resolve().parent.parent
    pasta_download = diretorio_destino

    # downloads/377/1250_2026
    pasta_destino = (
        diretorio_destino
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
            for arquivo in pasta_download.iterdir()
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
                for arquivo in pasta_download.iterdir()
                if arquivo.is_file()
            }

            novos = arquivos_agora - arquivos_antes
            extensoes_temporarias = {
                    ".crdownload",  # Chrome
                    ".tmp",         # temporário
                    ".part",        # Firefox/outros
                    ".partial",     # download parcial
                    ".download",    # alguns gerenciadores
                    ".temp",
                    ".!ut",         # uTorrent
                }
            # Ignora .crdownload
            completos = [
                arquivo
                for arquivo in novos
                if arquivo.suffix.lower() not in extensoes_temporarias
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


    
def aguardar_loader_desaparecer(driver, timeout=30):
    WebDriverWait(driver, timeout).until(
        EC.invisibility_of_element_located(
            (By.ID, "imgLoad")
        )
    )
    
