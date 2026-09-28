import shutil
import tempfile
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
    

def aguardar_arquivo_download(pasta, timeout=120):
    """Espera um único arquivo estabilizar, sem downloads parciais na pasta isolada."""
    temporarias = {".crdownload", ".tmp", ".part", ".partial", ".download", ".temp", ".!ut"}
    limite = time.monotonic() + timeout
    assinatura_anterior = None
    estavel_desde = None
    while time.monotonic() < limite:
        arquivos = [p for p in pasta.iterdir() if p.is_file()]
        completos = [p for p in arquivos if p.suffix.lower() not in temporarias]
        if len(completos) > 1:
            raise RuntimeError("Mais de um arquivo recebido para o mesmo anexo; download ambíguo.")
        assinatura = None
        if len(completos) == 1 and len(arquivos) == 1:
            try:
                estado = completos[0].stat()
                assinatura = (completos[0], estado.st_size, estado.st_mtime_ns)
            except FileNotFoundError:
                pass
        agora = time.monotonic()
        if assinatura is None or assinatura != assinatura_anterior:
            assinatura_anterior = assinatura
            estavel_desde = agora
        elif agora - estavel_desde >= 1:
            # No Windows, o Chrome ainda pode manter o arquivo bloqueado.
            try:
                with completos[0].open("rb"):
                    return completos[0]
            except PermissionError:
                pass
        time.sleep(0.25)
    raise TimeoutError(f"O arquivo do anexo não terminou de baixar em {timeout} segundos.")


def processar_contrato(driver, item, projeto, diretorio_destino):
    contrato = item["contrato"]
    diretorio_destino = Path(diretorio_destino).resolve()
    pasta_destino = diretorio_destino / str(projeto) / contrato.replace("/", "_")
    pasta_destino.mkdir(parents=True, exist_ok=True)
    pagina_anterior = driver.current_window_handle
    janelas_antes = set(driver.window_handles)
    janela_contrato = None
    pasta_download = None
    etapa = "abertura do contrato"
    try:
        aguardar_loader_desaparecer(driver)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item["link"])
        driver.execute_script("arguments[0].click();", item["link"])
        janela_contrato = WebDriverWait(driver, 30).until(
            lambda d: next((h for h in d.window_handles if h not in janelas_antes), False),
            message="A janela do contrato não abriu.",
        )
        driver.switch_to.window(janela_contrato)
        aguardar_loader_desaparecer(driver)
        etapa = "abertura da aba Arquivos"
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'a[href="#tabArquivo"]')
        )).click()
        aguardar_loader_desaparecer(driver)
        tabela_id = "ctl00_ContentPlaceHolder1_ConvenioContratoArquivosUserControl1_gvwArquivoContrato"
        tabela = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, tabela_id))
        )
        seletor = 'a[title="Baixar arquivo"]'
        quantidade = len(tabela.find_elements(By.CSS_SELECTOR, seletor))
        for indice in range(quantidade):
            etapa = f"download do anexo {indice + 1} de {quantidade}"
            aguardar_loader_desaparecer(driver)

            def localizar_botao(navegador):
                try:
                    tabela_atual = navegador.find_element(By.ID, tabela_id)
                    botoes = tabela_atual.find_elements(By.CSS_SELECTOR, seletor)
                    if len(botoes) != quantidade:
                        return False
                    botao = botoes[indice]
                    return botao if botao.is_displayed() and botao.is_enabled() else False
                except StaleElementReferenceException:
                    return False

            botao = WebDriverWait(driver, 30).until(localizar_botao)
            # Uma pasta exclusiva vincula o arquivo ao clique, inclusive com nomes repetidos.
            pasta_download = Path(tempfile.mkdtemp(prefix=".anexo-", dir=pasta_destino))
            driver.execute_cdp_cmd("Browser.setDownloadBehavior", {
                "behavior": "allow", "downloadPath": str(pasta_download),
            })
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao)
            botao.click()
            aguardar_loader_desaparecer(driver)
            arquivo = aguardar_arquivo_download(pasta_download)
            aguardar_loader_desaparecer(driver)
            destino = pasta_destino / arquivo.name
            if destino.exists():
                print(f"Arquivo já existe: {destino.name}")
                arquivo.unlink()
            else:
                shutil.move(str(arquivo), str(destino))
                print(f"Movido: {destino}")
            pasta_download.rmdir()
            pasta_download = None
    except Exception as erro:
        # Não inclui a exceção do navegador, que pode conter dados da sessão.
        print(f"Falha no contrato {contrato}: {etapa}.")
        raise RuntimeError(f"Falha no contrato {contrato}: {etapa}.") from erro
    finally:
        # Mantém arquivos parciais em caso de falha para não descartar anexos.
        try:
            driver.execute_cdp_cmd("Browser.setDownloadBehavior", {
                "behavior": "allow", "downloadPath": str(diretorio_destino),
            })
        finally:
            try:
                if janela_contrato is not None and janela_contrato in driver.window_handles:
                    driver.switch_to.window(janela_contrato)
                    driver.close()
            finally:
                driver.switch_to.window(pagina_anterior)


def aguardar_loader_desaparecer(driver, timeout=30):
    """Espera documento pronto e loader ausente continuamente por um segundo."""
    livre_desde = None

    def pagina_livre(navegador):
        nonlocal livre_desde
        try:
            pronta = navegador.execute_script("return document.readyState === 'complete';")
            loaders = navegador.find_elements(By.ID, "imgLoad")
            livre = pronta and not any(loader.is_displayed() for loader in loaders)
        except StaleElementReferenceException:
            livre = False
        if not livre:
            livre_desde = None
            return False
        agora = time.monotonic()
        if livre_desde is None:
            livre_desde = agora
        return agora - livre_desde >= 1

    WebDriverWait(driver, timeout, poll_frequency=0.2).until(
        pagina_livre, message="A página não terminou de carregar ou o loader continua visível.",
    )
