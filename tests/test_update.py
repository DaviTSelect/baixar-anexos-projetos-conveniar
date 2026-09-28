"""Consulta e downloads com respostas locais simuladas."""
import io
import json
from pathlib import Path
import tempfile
import unittest
from urllib.error import HTTPError, URLError
from unittest.mock import patch

from src import update


class UpdateTests(unittest.TestCase):
    def consultar(self, dados, atual='1.9.0'):
        with patch.object(update, 'VERSAO_ATUAL', atual), patch.object(
                update, 'urlopen', return_value=io.BytesIO(json.dumps(dados).encode())):
            return update.verificar_atualizacoes()

    def test_compara_numericamente_e_retorna_instalador(self):
        url = 'https://example.invalid/instalador.exe'
        release = {'tag_name': 'v1.10.0', 'assets': [
            {'name': 'notas.txt'}, {'name': 'instalador.exe', 'browser_download_url': url}]}
        texto, status, destino = self.consultar(release)
        self.assertEqual(status, update.STATUS_DISPONIVEL)
        self.assertEqual(destino, url)
        self.assertIn('1.10.0', texto)
        for versao in ('v1.9.0', 'v1.8.9'):
            with self.subTest(versao=versao):
                _, status, destino = self.consultar({'tag_name': versao})
                self.assertEqual(status, update.STATUS_ATUALIZADO)
                self.assertIsNone(destino)

    def test_respostas_invalidas_e_pre_releases(self):
        for dados in ([], {}, {'tag_name': None}, {'tag_name': 'v2.0.0-rc.1'},
                      {'tag_name': 'v2.0.0', 'prerelease': True},
                      {'tag_name': 'v2.0.0', 'draft': True}):
            with self.subTest(dados=dados):
                texto, status, url = self.consultar(dados)
                self.assertTrue(texto)
                self.assertEqual(status, update.STATUS_ERRO)
                self.assertIsNone(url)

    def test_nova_versao_sem_instalador_utilizavel_retorna_erro(self):
        for assets in ([], None, {}, [None], [{'name': 'app.zip'}], [{'name': 'app.exe'}]):
            with self.subTest(assets=assets):
                _, status, url = self.consultar({'tag_name': 'v2.0.0', 'assets': assets})
                self.assertEqual(status, update.STATUS_ERRO)
                self.assertIsNone(url)

    def test_falhas_de_rede_retornam_erro_para_o_inicializador(self):
        for erro in (TimeoutError(), URLError('offline'),
                     HTTPError(update.API_URL, 404, 'ausente', {}, None),
                     HTTPError(update.API_URL, 403, 'limite', {}, None)):
            with self.subTest(erro=erro), patch.object(update, 'urlopen', side_effect=erro):
                texto, status, url = update.verificar_atualizacoes()
                self.assertTrue(texto)
                self.assertEqual(status, update.STATUS_ERRO)
                self.assertIsNone(url)

    def test_json_invalido(self):
        with patch.object(update, 'urlopen', return_value=io.BytesIO(b'invalido')):
            self.assertEqual(update.verificar_atualizacoes()[1], update.STATUS_ERRO)

    def test_download_grava_conteudo_e_informa_progresso(self):
        for total in ('3', None, 'invalido'):
            with self.subTest(total=total), tempfile.TemporaryDirectory() as pasta:
                resposta = io.BytesIO(b'abc')
                resposta.headers = {'Content-Length': total}
                eventos = []
                with patch.object(update.tempfile, 'gettempdir', return_value=pasta), patch.object(
                        update, 'urlopen', return_value=resposta):
                    caminho = update.baixar_atualizacao(
                        'https://example.invalid/app.exe', lambda *args: eventos.append(args))
                self.assertEqual(Path(caminho).read_bytes(), b'abc')
                self.assertEqual(eventos[-1], (100, 3, 3) if total == '3' else (-1, 3, 0))

    def test_download_vazio_ou_interrompido_remove_arquivo(self):
        class Interrompida(io.BytesIO):
            def read(self, quantidade):
                if self.tell():
                    raise OSError('conexão interrompida')
                return super().read(quantidade)

        for resposta in (io.BytesIO(b''), Interrompida(b'parcial')):
            with self.subTest(resposta=resposta), tempfile.TemporaryDirectory() as pasta:
                resposta.headers = {}
                with patch.object(update.tempfile, 'gettempdir', return_value=pasta), patch.object(
                        update, 'urlopen', return_value=resposta):
                    with self.assertRaises(OSError):
                        update.baixar_atualizacao('https://example.invalid/app.exe')
                self.assertEqual(list(Path(pasta).iterdir()), [])

    def test_download_sem_url_nao_acessa_rede(self):
        with patch.object(update, 'urlopen') as abrir:
            with self.assertRaises(ValueError):
                update.baixar_atualizacao('')
        abrir.assert_not_called()
