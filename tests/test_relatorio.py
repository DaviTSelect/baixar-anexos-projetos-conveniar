"""Geração do relatório Excel de contratos processados."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

from src import update


class RelatórioTests(unittest.TestCase):
    def setUp(self):
        browser = types.ModuleType('browser')
        for nome in ('realizar_login', 'buscar_contratos', 'processar_contrato'):
            setattr(browser, nome, lambda *a, **k: None)
        spec = importlib.util.spec_from_file_location(
            'interface_relatorio', Path(__file__).resolve().parents[1] / 'src/interface.py')
        self.modulo = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'browser': browser, 'update': update}):
            spec.loader.exec_module(self.modulo)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base_dir = Path(self.temp.name)

    def gerar(self, projeto, resultados):
        with patch.object(self.modulo, 'BASE_DIR', self.base_dir):
            return self.modulo.gerar_relatorio(projeto, resultados)

    def test_cria_arquivo_no_base_dir(self):
        self.gerar(123, [])
        arquivos = list(self.base_dir.glob('relatorio_123_*.xlsx'))
        self.assertEqual(len(arquivos), 1)

    def test_nome_inclui_projeto_e_formato_timestamp(self):
        caminho = self.gerar(456, [])
        self.assertRegex(caminho.name, r'^relatorio_456_\d{8}_\d{6}\.xlsx$')

    def test_retorna_path(self):
        resultado = self.gerar(1, [])
        self.assertIsInstance(resultado, Path)

    def test_cabecalho_correto(self):
        import openpyxl
        caminho = self.gerar(1, [])
        ws = openpyxl.load_workbook(str(caminho)).active
        cabecalho = [ws.cell(1, c).value for c in range(1, 7)]
        self.assertEqual(cabecalho, [
            'Projeto', 'Contrato', 'Situacao', 'Resultado', 'Anexos Baixados', 'Detalhe'
        ])

    def test_lista_vazia_gera_so_cabecalho(self):
        import openpyxl
        caminho = self.gerar(99, [])
        ws = openpyxl.load_workbook(str(caminho)).active
        self.assertEqual(ws.max_row, 1)

    def test_dados_gravados_corretamente(self):
        import openpyxl
        resultados = [
            {'projeto': 100, 'contrato': '1/2026', 'situacao': 'Ativo',
             'resultado': 'Sucesso', 'baixados': 3, 'detalhe': ''},
            {'projeto': 100, 'contrato': '2/2026', 'situacao': 'Encerrado',
             'resultado': 'Erro', 'baixados': 0, 'detalhe': 'Falha na aba'},
            {'projeto': 100, 'contrato': '3/2026', 'situacao': 'Ativo',
             'resultado': 'Sem anexos', 'baixados': 0,
             'detalhe': 'Tabela de arquivos não encontrada'},
        ]
        caminho = self.gerar(100, resultados)
        ws = openpyxl.load_workbook(str(caminho)).active
        self.assertEqual(ws.max_row, 4)
        self.assertEqual(
            [ws.cell(2, c).value for c in range(1, 7)],
            [100, '1/2026', 'Ativo', 'Sucesso', 3, None]  # openpyxl lê '' como None
        )
        self.assertEqual(
            [ws.cell(3, c).value for c in range(1, 7)],
            [100, '2/2026', 'Encerrado', 'Erro', 0, 'Falha na aba']
        )
        self.assertEqual(
            [ws.cell(4, c).value for c in range(1, 7)],
            [100, '3/2026', 'Ativo', 'Sem anexos', 0, 'Tabela de arquivos não encontrada']
        )

    def test_tres_projetos_distintos_geram_arquivos_distintos(self):
        p1 = self.gerar(10, [])
        p2 = self.gerar(20, [])
        self.assertNotEqual(p1.name, p2.name)
        self.assertRegex(p1.name, r'^relatorio_10_')
        self.assertRegex(p2.name, r'^relatorio_20_')
