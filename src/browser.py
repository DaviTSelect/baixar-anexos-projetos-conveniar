"""Funções compartilhadas de navegação.

A implementação concreta dependerá da biblioteca de automação escolhida
(Selenium, Playwright ou equivalente).
"""


def aguardar_loader_desaparecer(page, timeout=30):
    """Aguarda o loader desaparecer antes de continuar.

    Implemente o seletor real do loader quando a interface for mapeada.
    """
    raise NotImplementedError(
        "Defina o seletor do loader e a estratégia de espera do navegador."
    )
