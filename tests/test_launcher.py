"""Inicializador obrigatório com GUI, rede e instalação simuladas."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import Mock, patch

import pytest

from src import launcher


class InicializadorTests(unittest.TestCase):
    def setUp(self):
        for alvo in ('tk.Tk', 'tk.Label', 'tk.Button',
                     'messagebox.showerror', 'messagebox.showwarning'):
            p = patch('src.launcher.' + alvo)
            p.start()
            self.addCleanup(p.stop)
        self.ui = launcher.Inicializador()

    def test_inicio_agenda_consulta_e_nao_libera_painel(self):
        self.assertFalse(self.ui.iniciar())
        self.ui.app.mainloop.assert_called_once()
        self.assertIn(self.ui.verificar, [c.args[1] for c in self.ui.app.after.call_args_list])

    def test_versao_atualizada_agenda_abertura_uma_unica_vez(self):
        with patch.object(launcher, 'verificar_atualizacoes',
                          return_value=('Atualizado', launcher.STATUS_ATUALIZADO, None)):
            self.ui.status.configure.reset_mock()
            self.ui.executar_verificacao()
        self.ui.status.configure.assert_not_called()
        self.ui.consumir_eventos()
        self.assertFalse(self.ui.pode_iniciar_programa)
        self.assertIn(self.ui.abrir_programa, [c.args[1] for c in self.ui.app.after.call_args_list])
        self.ui.abrir_programa()
        self.ui.abrir_programa()
        self.assertTrue(self.ui.pode_iniciar_programa)
        self.ui.app.destroy.assert_called_once()

    def test_erro_ou_status_desconhecido_permite_tentar_sem_abrir_painel(self):
        for status in (launcher.STATUS_ERRO, 'desconhecido'):
            with self.subTest(status=status):
                self.ui.eventos.put(('verificacao', ('Falha fictícia', status, None)))
                self.ui.consumir_eventos()
                self.assertFalse(self.ui.pode_iniciar_programa)
                self.assertTrue(self.ui.botao_visivel)
        self.ui.app.destroy.assert_not_called()

    def test_excecao_na_consulta_chega_pela_fila(self):
        with patch.object(launcher, 'verificar_atualizacoes', side_effect=RuntimeError('falha fictícia')):
            self.ui.executar_verificacao()
        tipo, resultado = self.ui.eventos.get_nowait()
        self.assertEqual(tipo, 'verificacao')
        self.assertEqual(resultado[1:], (launcher.STATUS_ERRO, None))

    def test_nova_versao_inicia_download_sem_liberar_painel(self):
        url = 'https://example.invalid/app.exe'
        with patch.object(launcher, 'Thread') as thread:
            self.ui.eventos.put(('verificacao', ('Nova versão', launcher.STATUS_DISPONIVEL, url)))
            self.ui.consumir_eventos()
            self.ui.iniciar_download()
        self.assertTrue(self.ui.baixando)
        self.assertEqual(self.ui.url_download, url)
        self.assertFalse(self.ui.pode_iniciar_programa)
        thread.return_value.start.assert_called_once()

    def test_download_publica_progresso_e_resultado_sem_tocar_widgets(self):
        def baixar(url, progresso):
            progresso(50, 5, 10)
            return 'C:/ficticio/instalador.exe'
        self.ui.url_download = 'https://example.invalid/app.exe'
        with patch.object(launcher, 'baixar_atualizacao', side_effect=baixar):
            self.ui.executar_download()
        self.ui.status.configure.assert_not_called()
        self.assertEqual(self.ui.eventos.get_nowait(), ('progresso', 50, 5, 10))
        self.ui.consumir_eventos()
        self.assertEqual(self.ui.arquivo_download, 'C:/ficticio/instalador.exe')
        self.assertIn(self.ui.instalar, [c.args[1] for c in self.ui.app.after.call_args_list])
        self.assertFalse(self.ui.pode_iniciar_programa)

    def test_falha_de_download_permite_nova_tentativa(self):
        self.ui.baixando = True
        self.ui.url_download = 'https://example.invalid/app.exe'
        with patch.object(launcher, 'baixar_atualizacao', side_effect=OSError('falha fictícia')):
            self.ui.executar_download()
        self.ui.consumir_eventos()
        self.assertFalse(self.ui.baixando)
        self.assertTrue(self.ui.botao_visivel)
        self.assertFalse(self.ui.pode_iniciar_programa)
        launcher.messagebox.showerror.assert_called_once()

    def test_instalacao_abre_arquivo_e_encerra_sem_abrir_versao_antiga(self):
        self.ui.arquivo_download = 'C:/ficticio/instalador.exe'
        with patch.object(launcher.sys, 'platform', 'win32'), patch.object(
                launcher.os, 'startfile', create=True) as abrir:
            self.ui.instalar()
        abrir.assert_called_once_with(self.ui.arquivo_download)
        self.assertFalse(self.ui.pode_iniciar_programa)
        self.ui.app.destroy.assert_called_once()

    def test_falha_ao_iniciar_instalador_nao_libera_programa(self):
        self.ui.arquivo_download = 'C:/ficticio/instalador.exe'
        with patch.object(launcher.sys, 'platform', 'win32'), patch.object(
                launcher.os, 'startfile', side_effect=OSError('falha fictícia'), create=True):
            self.ui.instalar()
        self.assertFalse(self.ui.pode_iniciar_programa)
        self.assertTrue(self.ui.botao_visivel)
        self.ui.app.destroy.assert_not_called()
        launcher.messagebox.showerror.assert_called_once()

    def test_fechar_durante_download_e_bloqueado(self):
        self.ui.baixando = True
        self.ui.fechar()
        self.ui.app.destroy.assert_not_called()
        launcher.messagebox.showwarning.assert_called_once()

    def test_fechar_fora_do_download_ignora_resultados_tardios(self):
        self.ui.fechar()
        self.ui.eventos.put(('verificacao', ('Atualizado', launcher.STATUS_ATUALIZADO, None)))
        self.ui.consumir_eventos()
        self.assertFalse(self.ui.pode_iniciar_programa)
        self.ui.status.configure.assert_not_called()
        self.ui.app.destroy.assert_called_once()

    @pytest.mark.xfail(strict=True, reason='QA-01: verificar() não impede consultas simultâneas; ver docs/testes.md')
    def test_consultas_simultaneas_devem_ser_impedidas(self):
        with patch.object(launcher, 'Thread') as thread:
            self.ui.verificar()
            self.ui.verificar()
        thread.return_value.start.assert_called_once()

    def test_entrada_principal_respeita_escolha(self):
        interface = types.ModuleType('interface')
        interface.InterfaceAutomacao = Mock()
        spec = importlib.util.spec_from_file_location(
            'main_teste', Path(__file__).resolve().parents[1] / 'src/main.py')
        modulo = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'launcher': launcher, 'interface': interface}):
            spec.loader.exec_module(modulo)
            with patch.object(modulo, 'Inicializador') as inicializador:
                inicializador.return_value.iniciar.return_value = False
                modulo.main()
                interface.InterfaceAutomacao.assert_not_called()
                inicializador.return_value.iniciar.return_value = True
                modulo.main()
        interface.InterfaceAutomacao.assert_called_once()
        interface.InterfaceAutomacao.return_value.iniciar.assert_called_once()
