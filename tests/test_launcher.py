"""Fluxo inicial sem janela, rede ou credenciais reais."""
import importlib.util
from pathlib import Path
import sys
from threading import Event
import types
import unittest
from unittest.mock import Mock, patch

from src import launcher


class InicializadorTests(unittest.TestCase):
    def setUp(self):
        self.patches = [patch.object(launcher.tk, 'Tk'),
                        patch.object(launcher.tk, 'Label'),
                        patch.object(launcher.tk, 'Button')]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)
        self.ui = launcher.Inicializador()

    def test_continuar_sem_consultar_e_apenas_uma_vez(self):
        with patch.object(launcher, 'verificar_atualizacoes') as consulta:
            self.ui.continuar()
            self.ui.continuar()
        consulta.assert_not_called()
        self.assertTrue(self.ui.iniciar())
        self.ui.app.destroy.assert_called_once()
        self.ui.app.after_cancel.assert_called_once()

    def test_fechar_nao_abre_painel(self):
        self.ui.fechar()
        self.assertFalse(self.ui.iniciar())

    def test_continuar_durante_consulta_sem_esperar_rede(self):
        entrou, liberar, terminou = Event(), Event(), Event()

        def consulta():
            entrou.set()
            liberar.wait(5)
            terminou.set()
            return 'Atualização disponível', True

        with patch.object(launcher, 'verificar_atualizacoes', side_effect=consulta) as verificar:
            try:
                self.ui.verificar()
                self.assertTrue(entrou.wait(3))
                self.ui.verificar()
                verificar.assert_called_once()
                self.ui.status.configure.reset_mock()
                self.ui.continuar()
                self.ui.app.destroy.assert_called_once()
                self.assertFalse(terminou.is_set())
            finally:
                liberar.set()
                self.assertTrue(terminou.wait(3))
        self.ui.consumir_eventos()
        self.ui.status.configure.assert_not_called()

    def test_resultados_chegam_a_interface_pela_fila(self):
        for disponivel in (True, False):
            with self.subTest(disponivel=disponivel), patch.object(
                    launcher, 'verificar_atualizacoes', return_value=('Resultado', disponivel)):
                self.ui.status.configure.reset_mock()
                self.ui.executar()
                self.ui.status.configure.assert_not_called()
                self.ui.consumir_eventos()
                self.ui.status.configure.assert_called_once_with(text='Resultado')
                self.assertEqual(self.ui.disponivel, disponivel)
                self.assertFalse(self.ui.consultando)

    def test_falha_inesperada_permite_continuar_sem_expor_excecao(self):
        with patch.object(launcher, 'verificar_atualizacoes', side_effect=RuntimeError('segredo')):
            self.ui.executar()
        self.ui.consumir_eventos()
        self.assertNotIn('segredo', str(self.ui.status.configure.call_args))
        self.assertFalse(self.ui.disponivel)
        self.ui.continuar()
        self.assertTrue(self.ui.usar_atual)

    def test_download_manual_so_quando_disponivel(self):
        with patch.object(launcher.webbrowser, 'open', return_value=True) as abrir:
            self.ui.abrir_release()
            abrir.assert_not_called()
            self.ui.disponivel = True
            self.ui.abrir_release()
            abrir.assert_called_once_with(launcher.RELEASES_URL)
        self.ui.app.destroy.assert_not_called()

    def test_falha_ao_abrir_navegador_informa_endereco(self):
        self.ui.disponivel = True
        with patch.object(launcher.webbrowser, 'open', return_value=False), patch.object(
                launcher.messagebox, 'showwarning') as aviso:
            self.ui.abrir_release()
        self.assertIn(launcher.RELEASES_URL, str(aviso.call_args))

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
