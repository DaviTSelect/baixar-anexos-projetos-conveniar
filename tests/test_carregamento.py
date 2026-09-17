"""Regressões da espera das linhas, sem login ou acesso ao .env."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException


class CarregamentoTests(unittest.TestCase):
    def test_login_fecha_navegador_quando_navegacao_falha(self):
        driver = Mock()
        driver.get.side_effect = RuntimeError('falha simulada')
        with patch.dict(self.browser.os.environ, {'USERPROFILE': 'C:/ficticio'}), \
                patch.object(self.browser.os.path, 'isfile', return_value=True), \
                patch.object(self.browser.webdriver, 'Chrome', return_value=driver):
            with self.assertRaises(RuntimeError):
                self.browser.realizar_login(Mock())
        driver.quit.assert_called_once()

    def test_driver_ausente_gera_excecao_sem_interface_grafica(self):
        with patch.dict(self.browser.os.environ, {'USERPROFILE': 'C:/ficticio'}), \
                patch.object(self.browser.os.path, 'isfile', return_value=False):
            with self.assertRaises(FileNotFoundError):
                self.browser.realizar_login(Mock())

    def setUp(self):
        config = types.ModuleType('config')
        config.URL = config.USUARIO = config.SENHA = ''
        config.HEADLESS = True
        spec = importlib.util.spec_from_file_location(
            'browser_em_teste', Path(__file__).resolve().parents[1] / 'src/browser.py'
        )
        self.browser = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'config': config}):
            spec.loader.exec_module(self.browser)
        self.driver = Mock()
        self.driver.execute_script.return_value = {
            'carregada': True, 'altura': 1000, 'noFinal': True,
        }
        self.driver.find_element.return_value.is_displayed.return_value = False
        self.primeira = Mock(id='1', text='Contrato 1')
        self.segunda = Mock(id='2', text='Contrato 2')

    def executar(self, estados, timeout=8):
        self.driver.find_elements.side_effect = estados
        relogio = [0.0]

        def avancar(segundos):
            relogio[0] += segundos

        with patch.object(self.browser.time, 'monotonic', side_effect=lambda: relogio[0]), \
                patch.object(self.browser.time, 'sleep', side_effect=avancar):
            return self.browser.carregar_linhas_contratos(self.driver, timeout=timeout)

    def test_rebusca_inclui_linha_tardia_e_preserva_primeira(self):
        completas = [self.primeira, self.segunda]
        resultado = self.executar([[self.primeira]] * 3 + [completas] * 5)
        self.assertEqual(resultado, completas)
        self.assertEqual(self.driver.find_elements.call_count, 8)

    def test_tabela_vazia_estavel(self):
        self.assertEqual(self.executar([[]] * 5), [])

    def test_recupera_linhas_substituidas(self):
        resultado = self.executar(
            [[self.primeira], StaleElementReferenceException()] + [[self.segunda]] * 5
        )
        self.assertEqual(resultado, [self.segunda])

    def test_loader_visivel_impede_processamento(self):
        self.driver.find_element.return_value.is_displayed.return_value = True
        with self.assertRaises(TimeoutException):
            self.executar([], timeout=3)
        self.driver.find_elements.assert_not_called()

    def test_pagina_crescendo_nao_estabiliza(self):
        self.driver.execute_script.side_effect = [
            {'carregada': True, 'altura': altura, 'noFinal': True}
            for altura in range(1000, 1020)
        ]
        with self.assertRaises(TimeoutException):
            self.executar([[self.primeira]] * 20, timeout=3)

    def test_documento_incompleto_ou_fora_do_final_impede_processamento(self):
        for estado in (
            {'carregada': False, 'altura': 1000, 'noFinal': True},
            {'carregada': True, 'altura': 1000, 'noFinal': False},
        ):
            with self.subTest(estado=estado):
                self.driver.execute_script.return_value = estado
                with self.assertRaises(TimeoutException):
                    self.executar([], timeout=3)
        self.driver.find_elements.assert_not_called()
