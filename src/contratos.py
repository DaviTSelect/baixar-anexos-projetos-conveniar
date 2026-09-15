"""Regras relacionadas aos contratos."""

SITUACOES_PERMITIDAS = {"ATIVO", "ENCERRADO"}


def normalizar_situacao(situacao: str) -> str:
    """Normaliza a situação exibida na tabela."""
    if not isinstance(situacao, str):
        return ""
    return situacao.strip().upper()


def situacao_valida(situacao: str) -> bool:
    """Retorna True somente para contratos ATIVO ou ENCERRADO."""
    return normalizar_situacao(situacao) in SITUACOES_PERMITIDAS
