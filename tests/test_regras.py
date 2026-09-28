"""Regras da consulta real com navegador simulado, sem acesso ao .env."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch


class RegrasTests(unittest.TestCase):
    def setUp(self):
        config = types.ModuleType('config')
        config.URL = config.USUARIO = config.SENHA = ''
        config.HEADLESS = True
        spec = importlib.util.spec_from_file_location(
            'browser_regras', Path(__file__).resolve().parents[1] / 'src/browser.py')
        self.browser = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'config': config}):
            spec.loader.exec_module(self.browser)

    def linha(self, status='ATIVO', projeto='377 - Projeto fictício', link=True):
        colunas = [Mock(text='') for _ in range(11)]
        colunas[1].text = ' 1250/2026 '
        colunas[1].find_elements.return_value = [Mock()] if link else []
        colunas[2].text = projeto
        colunas[10].text = status
        return Mock(find_elements=Mock(return_value=colunas))

    def consultar(self, linhas):
        with patch.object(self.browser, 'WebDriverWait'), patch.object(
                self.browser, 'aguardar_loader_desaparecer'), patch.object(
                self.browser, 'carregar_linhas_contratos', return_value=linhas):
            return self.browser.buscar_contratos(Mock(), 377)

    def test_aceita_ativo_encerrado_e_normaliza_extremidades(self):
        for status in ('ATIVO', 'ENCERRADO', ' ativo ', ' EnCeRrAdO '):
            with self.subTest(status=status):
                linha = self.linha(status=status)
                resultado = self.consultar([linha])
                self.assertEqual(len(resultado), 1)
                self.assertEqual(resultado[0]['contrato'], '1250/2026')
                self.assertIs(resultado[0]['link'],
                              linha.find_elements.return_value[1].find_elements.return_value[0])

    def test_rejeita_situacoes_fora_do_escopo(self):
        for status in ('CANCELADO', 'SUSPENSO', '', 'ATIVO PENDENTE'):
            with self.subTest(status=status):
                self.assertEqual(self.consultar([self.linha(status=status)]), [])

    def test_rejeita_outro_projeto_linha_incompleta_e_sem_link(self):
        linhas = [self.linha(projeto='1377 - Outro'),
                  self.linha(projeto='3770 - Outro'), self.linha(link=False),
                  Mock(find_elements=Mock(return_value=[Mock()] * 10))]
        self.assertEqual(self.consultar(linhas), [])

    def test_preserva_ordem_dos_validos_entre_linhas_ignoradas(self):
        primeira, segunda = self.linha(), self.linha(status='ENCERRADO')
        segunda.find_elements.return_value[1].text = '1251/2026'
        resultado = self.consultar([primeira, self.linha(status='CANCELADO'), segunda])
        self.assertEqual([item['contrato'] for item in resultado], ['1250/2026', '1251/2026'])

    def test_consulta_sem_linhas(self):
        self.assertEqual(self.consultar([]), [])
