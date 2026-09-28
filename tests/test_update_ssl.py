"""Regressões de TLS sem rede nem downloads reais."""

import io
import json
from pathlib import Path
import ssl
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError

from src import update


class UpdateSSLTests(unittest.TestCase):
    def test_contexto_preserva_cas_do_sistema_e_acrescenta_certifi(self):
        sistema = ssl.create_default_context()
        cas_sistema = set(sistema.get_ca_certs(binary_form=True))
        pacote = ssl.create_default_context(cafile=update.certifi.where())
        with patch.object(update.ssl, 'create_default_context', return_value=sistema):
            contexto = update._contexto_ssl()
        cas = set(contexto.get_ca_certs(binary_form=True))
        self.assertTrue(cas_sistema.issubset(cas))
        self.assertTrue(set(pacote.get_ca_certs(binary_form=True)).issubset(cas))
        self.assertGreater(len(cas), 0)
        self.assertEqual(contexto.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(contexto.check_hostname)

    def conferir_tls(self, abrir):
        contexto = abrir.call_args.kwargs['context']
        self.assertEqual(contexto.verify_mode, ssl.CERT_REQUIRED)
        self.assertTrue(contexto.check_hostname)
        self.assertGreater(contexto.cert_store_stats()['x509_ca'], 0)

    def test_consulta_usa_tls_verificado(self):
        dados = {'tag_name': update.VERSAO_ATUAL}
        with patch.object(update, 'urlopen', return_value=io.BytesIO(
                json.dumps(dados).encode())) as abrir:
            _, status, url = update.verificar_atualizacoes()
        self.assertEqual(status, update.STATUS_ATUALIZADO)
        self.assertIsNone(url)
        self.conferir_tls(abrir)

    def test_download_usa_tls_verificado(self):
        resposta = io.BytesIO(b'arquivo ficticio')
        resposta.headers = {'Content-Length': '16'}
        with tempfile.TemporaryDirectory() as pasta, patch.object(
                update.tempfile, 'gettempdir', return_value=pasta), patch.object(
                update, 'urlopen', return_value=resposta) as abrir:
            caminho = update.baixar_atualizacao('https://example.invalid/app.exe')
            self.assertEqual(Path(caminho).read_bytes(), b'arquivo ficticio')
        self.conferir_tls(abrir)

    def test_certificado_invalido_nao_provoca_tentativa_sem_validacao(self):
        erro = URLError(ssl.SSLCertVerificationError('certificado ficticio invalido'))
        with patch.object(update, 'urlopen', side_effect=erro) as abrir:
            _, status, url = update.verificar_atualizacoes()
            self.assertEqual(status, update.STATUS_ERRO)
            self.assertIsNone(url)
            self.assertEqual(abrir.call_count, 1)
            self.conferir_tls(abrir)
        with tempfile.TemporaryDirectory() as pasta, patch.object(
                update.tempfile, 'gettempdir', return_value=pasta), patch.object(
                update, 'urlopen', side_effect=erro) as abrir:
            with self.assertRaises(URLError):
                update.baixar_atualizacao('https://example.invalid/app.exe')
            self.assertEqual(list(Path(pasta).iterdir()), [])
            self.assertEqual(abrir.call_count, 1)
            self.conferir_tls(abrir)
