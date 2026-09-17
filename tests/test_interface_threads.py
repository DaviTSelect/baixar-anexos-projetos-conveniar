"""Valida concorrência sem abrir o Conveniar nem ler credenciais."""
import importlib.util
from pathlib import Path
from queue import Queue
import sys
from threading import Event, Thread, get_ident
import types
import unittest
from unittest.mock import Mock, patch
from tempfile import TemporaryDirectory

from src import update


class InterfaceTests(unittest.TestCase):
    def setUp(self):
        browser = types.ModuleType('browser')
        for nome in ('realizar_login', 'buscar_contratos', 'processar_contrato'):
            setattr(browser, nome, Mock())
        spec = importlib.util.spec_from_file_location(
            'interface_teste', Path(__file__).resolve().parents[1] / 'src/interface.py')
        self.modulo = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'browser': browser, 'update': update}):
            spec.loader.exec_module(self.modulo)
        self.ui = self.modulo.InterfaceAutomacao.__new__(self.modulo.InterfaceAutomacao)
        self.ui.eventos = Queue()
        self.ui.cancelar = Event()
        self.ui.executando = self.ui.fechando = False
        self.ui.worker = None
        self.ui.numero_projeto = 123
        self.pasta = TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)
        self.ui.diretorio = Path(self.pasta.name)
        for nome in ('app', 'label_status', 'label_atualizacao', 'botao_atualizacao',
                     'botao_conferir_N_projeto', 'campo_N_projeto'):
            setattr(self.ui, nome, Mock())
        self.driver = self.modulo.realizar_login.return_value
        self.modulo.buscar_contratos.return_value = [{'contrato': '1/2026'}]

    def test_janela_livre_sem_acesso_a_widgets_pelo_worker(self):
        entrou, liberar = Event(), Event()
        threads = []
        def processar(*args):
            threads.append(get_ident())
            entrou.set()
            self.assertTrue(liberar.wait(5))
        self.modulo.processar_contrato.side_effect = processar
        self.ui.botao_iniciar_processo()
        try:
            self.assertTrue(entrou.wait(3))
            self.ui.botao_iniciar_processo()
            self.modulo.realizar_login.assert_called_once_with()
            self.ui.label_status.configure.assert_not_called()
            self.ui.app.after.assert_not_called()
            self.assertNotEqual(threads[0], get_ident())
        finally:
            liberar.set()
            self.ui.worker.join(5)
        self.driver.quit.assert_called_once()
        with patch.object(self.modulo.messagebox, 'showinfo') as aviso:
            self.ui.consumir_eventos()
        aviso.assert_called_once()
        self.assertFalse(self.ui.executando)

    def test_falha_fecha_driver_e_avisa_so_na_thread_principal(self):
        self.modulo.buscar_contratos.side_effect = RuntimeError('segredo fictício')
        with patch.object(self.modulo.messagebox, 'showerror') as aviso:
            self.ui.executar_automacao(123, self.ui.diretorio)
            aviso.assert_not_called()
            self.ui.consumir_eventos()
        self.driver.quit.assert_called_once()
        self.assertNotIn('segredo', str(aviso.call_args))
        self.assertIn('consulta dos contratos', str(aviso.call_args))

    def test_fechar_aguarda_worker_e_nao_inicia_outro_contrato(self):
        self.modulo.buscar_contratos.return_value *= 2
        self.modulo.processar_contrato.side_effect = lambda *args: self.ui.cancelar.set()
        self.ui.executar_automacao(123, self.ui.diretorio)
        self.modulo.processar_contrato.assert_called_once()
        self.driver.quit.assert_called_once()
        self.ui.worker = Mock()
        self.ui.worker.is_alive.return_value = True
        self.ui.fechar()
        self.ui.consumir_eventos()
        self.ui.app.destroy.assert_not_called()
        self.ui.worker.is_alive.return_value = False
        self.ui.consumir_eventos()
        self.ui.app.destroy.assert_called_once()

    def test_falha_no_quit_nao_anuncia_sucesso(self):
        self.driver.quit.side_effect = RuntimeError('falha')
        self.ui.executar_automacao(123, self.ui.diretorio)
        with patch.object(self.modulo.messagebox, 'showerror') as erro, \
                patch.object(self.modulo.messagebox, 'showinfo') as sucesso:
            self.ui.consumir_eventos()
        erro.assert_called_once()
        sucesso.assert_not_called()


if __name__ == '__main__':
    unittest.main()
