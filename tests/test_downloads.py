"""Downloads simulados, sem credenciais ou acesso ao Conveniar."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

from selenium.common.exceptions import TimeoutException


class DownloadsTests(unittest.TestCase):
    def setUp(self):
        config = types.ModuleType('config')
        config.URL = config.USUARIO = config.SENHA = ''
        config.HEADLESS = True
        spec = importlib.util.spec_from_file_location(
            'browser_download_test', Path(__file__).resolve().parents[1] / 'src/browser.py'
        )
        self.browser = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'config': config}):
            spec.loader.exec_module(self.browser)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.pasta = Path(self.temp.name)
        self.agora = 0
        self.addCleanup(patch.stopall)
        patch.object(self.browser.time, 'monotonic', side_effect=lambda: self.agora).start()
        patch.object(self.browser.time, 'sleep', side_effect=self.avancar).start()

    def avancar(self, segundos):
        self.agora += segundos

    def test_espera_renomeacao_do_parcial_e_crescimento(self):
        parcial = self.pasta / 'documento.pdf.crdownload'
        final = self.pasta / 'documento.pdf'
        parcial.write_bytes(b'inicio')

        def baixar(segundos):
            self.avancar(segundos)
            if self.agora >= 1 and parcial.exists():
                parcial.rename(final)
            if 1 <= self.agora <= 2:
                with final.open('ab') as arquivo:
                    arquivo.write(b'mais')

        with patch.object(self.browser.time, 'sleep', side_effect=baixar):
            self.assertEqual(self.browser.aguardar_arquivo_download(self.pasta), final)
        self.assertGreaterEqual(self.agora, 3)

    def test_timeout_nao_aceita_parcial_nem_apaga_arquivo(self):
        parcial = self.pasta / 'arquivo.crdownload'
        parcial.write_bytes(b'parcial')
        with self.assertRaises(TimeoutError):
            self.browser.aguardar_arquivo_download(self.pasta, timeout=2)
        self.assertTrue(parcial.exists())

    def test_nao_escolhe_arquivo_arbitrario(self):
        for nome in ('a.pdf', 'b.pdf'):
            (self.pasta / nome).write_bytes(b'teste')
        with self.assertRaises(RuntimeError):
            self.browser.aguardar_arquivo_download(self.pasta)

    def test_loader_tardio_reinicia_espera(self):
        driver = Mock()
        driver.execute_script.return_value = True
        loader = Mock()
        loader.is_displayed.side_effect = lambda: 0.4 <= self.agora < 1.2
        driver.find_elements.return_value = [loader]
        self.browser.aguardar_loader_desaparecer(driver)
        self.assertGreaterEqual(self.agora, 2.2)

    def test_loader_visivel_gera_timeout(self):
        driver = Mock()
        driver.execute_script.return_value = True
        driver.find_elements.return_value = [Mock()]
        with self.assertRaises(TimeoutException):
            self.browser.aguardar_loader_desaparecer(driver, timeout=2)

    def preparar_contrato(self, nomes, falhar=False):
        driver = Mock()
        driver.current_window_handle = 'consulta'
        driver.window_handles = ['consulta']
        destino_atual = [None]
        tabela = Mock()
        botoes = [Mock() for _ in nomes]
        tabela.find_elements.return_value = botoes
        aba = Mock()
        aba.is_displayed.return_value = True
        aba.is_enabled.return_value = True
        driver.find_element.side_effect = lambda by, valor: aba if valor.startswith('a[') else tabela

        def executar_script(script, *args):
            if 'click()' in script:
                driver.window_handles = ['consulta', 'contrato']

        def configurar(comando, parametros):
            destino_atual[0] = Path(parametros['downloadPath'])

        driver.execute_script.side_effect = executar_script
        driver.execute_cdp_cmd.side_effect = configurar
        for indice, (botao, nome) in enumerate(zip(botoes, nomes)):
            def baixar(indice=indice, nome=nome):
                if indice:
                    self.assertTrue((self.pasta / '328' / '10_2026' / nomes[indice - 1]).exists())
                if falhar:
                    raise RuntimeError('falha simulada')
                (destino_atual[0] / nome).write_bytes(str(indice).encode())
            botao.click.side_effect = baixar
        return driver, botoes

    def test_varios_anexos_isolados_e_colisao_preserva_existente(self):
        destino = self.pasta / '328' / '10_2026'
        destino.mkdir(parents=True)
        (destino / 'a.pdf').write_bytes(b'original')
        (self.pasta / 'alheio.pdf').write_bytes(b'fora')
        driver, botoes = self.preparar_contrato(['a.pdf', 'b.pdf', 'c.pdf'])
        with patch.object(self.browser, 'aguardar_loader_desaparecer'):
            self.browser.processar_contrato(driver, {'contrato': '10/2026', 'link': Mock()}, 328, self.pasta)
        self.assertEqual({p.name for p in destino.iterdir()}, {'a.pdf', 'b.pdf', 'c.pdf'})
        self.assertEqual((destino / 'a.pdf').read_bytes(), b'original')
        self.assertEqual((destino / 'b.pdf').read_bytes(), b'1')
        self.assertEqual((self.pasta / 'alheio.pdf').read_bytes(), b'fora')
        for botao in botoes:
            botao.click.assert_called_once()
        driver.close.assert_called_once()
        driver.switch_to.window.assert_called_with('consulta')

    def test_tabela_sem_botoes_encerra_contrato_sem_download(self):
        driver, _ = self.preparar_contrato([])
        with patch.object(self.browser, 'aguardar_loader_desaparecer'), patch.object(
                self.browser, 'aguardar_arquivo_download') as aguardar:
            self.browser.processar_contrato(
                driver, {'contrato': '10/2026', 'link': Mock()}, 328, self.pasta)
        aguardar.assert_not_called()
        driver.close.assert_called_once()
        driver.switch_to.window.assert_called_with('consulta')

    def test_tabela_ausente_propaga_falha_e_restaura_navegacao(self):
        # A ausência completa da tabela ainda não é tratada como contrato sem anexos.
        driver, _ = self.preparar_contrato([])
        localizar = driver.find_element.side_effect

        def encontrar(by, valor):
            if 'gvwArquivoContrato' in valor:
                raise TimeoutException('tabela ausente')
            return localizar(by, valor)

        driver.find_element.side_effect = encontrar
        with patch.object(self.browser, 'aguardar_loader_desaparecer'):
            with self.assertRaisesRegex(RuntimeError, 'abertura da aba Arquivos'):
                self.browser.processar_contrato(
                    driver, {'contrato': '10/2026', 'link': Mock()}, 328, self.pasta)
        driver.close.assert_called_once()
        driver.switch_to.window.assert_called_with('consulta')

    def test_falha_restaura_janela_e_pasta(self):
        driver, _ = self.preparar_contrato(['a.pdf'], falhar=True)
        with patch.object(self.browser, 'aguardar_loader_desaparecer'):
            with self.assertRaisesRegex(RuntimeError, 'anexo 1 de 1'):
                self.browser.processar_contrato(driver, {'contrato': '10/2026', 'link': Mock()}, 328, self.pasta)
        driver.close.assert_called_once()
        driver.switch_to.window.assert_called_with('consulta')
        self.assertEqual(driver.execute_cdp_cmd.call_args.args[1]['downloadPath'], str(self.pasta.resolve()))
