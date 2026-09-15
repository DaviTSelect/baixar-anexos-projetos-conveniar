"""Funções compartilhadas de navegação.

A implementação concreta dependerá da biblioteca de automação escolhida
(Selenium, Playwright ou equivalente).
"""
def realizar_login():
    #login aqui

def buscar_contratos():
    #funcao de selecionar tipo de contrato
    #funcao de inserir nome do projeto
    #funcao de limpeza de data
    #funcao de buscar
    #contrato = {href,projeto,tipo,situacao}

    return lista_contratos

def processar_projetos():
    # pra cada pagina que existir
    # verifica situacao do projeto
    # abre o projeto
    # clique em arquivos
    # procure anexos e baixe todos os anexos
    # coloque todos os anexos dentro da pasta do projeto/contrato


def aguardar_loader_desaparecer(page, timeout=30):
    """Aguarda o loader desaparecer antes de continuar.

    Implemente o seletor real do loader quando a interface for mapeada.
    """
    raise NotImplementedError(
        "Defina o seletor do loader e a estratégia de espera do navegador."
    )
