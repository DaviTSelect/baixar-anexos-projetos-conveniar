import io
import json
import unittest
from urllib.error import HTTPError, URLError
from unittest.mock import patch

from src import update


class UpdateTests(unittest.TestCase):
    def consultar(self, dados, atual='1.9.0'):
        with patch.object(update, 'VERSAO_ATUAL', atual), patch.object(
                update, 'urlopen', return_value=io.BytesIO(json.dumps(dados).encode())) as abrir:
            resultado = update.verificar_atualizacoes()
        self.assertEqual(abrir.call_args.kwargs['timeout'], 10)
        return resultado

    def test_compara_numericamente(self):
        self.assertTrue(self.consultar({'tag_name': 'v1.10.0'})[1])
        self.assertFalse(self.consultar({'tag_name': 'v1.9.0'})[1])
        self.assertFalse(self.consultar({'tag_name': 'v1.8.9'})[1])

    def test_respostas_invalidas_e_pre_releases(self):
        for dados in ([], {}, {'tag_name': None}, {'tag_name': 'v2.0.0-rc.1'},
                      {'tag_name': 'v2.0.0', 'prerelease': True},
                      {'tag_name': 'v2.0.0', 'draft': True}):
            with self.subTest(dados=dados):
                self.assertFalse(self.consultar(dados)[1])

    def test_falhas_de_rede_nao_interrompem_aplicativo(self):
        for erro in (TimeoutError(), URLError('offline'),
                     HTTPError(update.API_URL, 404, 'ausente', {}, None),
                     HTTPError(update.API_URL, 403, 'limite', {}, None)):
            with self.subTest(erro=erro), patch.object(update, 'urlopen', side_effect=erro):
                texto, disponivel = update.verificar_atualizacoes()
                self.assertTrue(texto)
                self.assertFalse(disponivel)

    def test_json_invalido(self):
        with patch.object(update, 'urlopen', return_value=io.BytesIO(b'invalido')):
            self.assertFalse(update.verificar_atualizacoes()[1])


if __name__ == '__main__':
    unittest.main()
