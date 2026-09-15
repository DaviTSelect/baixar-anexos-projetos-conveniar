from src.contratos import normalizar_situacao, situacao_valida


def test_ativo_e_encerrado_sao_validos():
    assert situacao_valida("ATIVO")
    assert situacao_valida("ENCERRADO")


def test_outras_situacoes_sao_ignoradas():
    assert not situacao_valida("CANCELADO")
    assert not situacao_valida("SUSPENSO")


def test_normalizacao():
    assert normalizar_situacao(" ativo ") == "ATIVO"
    assert situacao_valida(" encerrado ")
