"""Configuração básica de logging para o projeto."""

import logging


def configurar_logger():
    """Cria e configura um logger único para a aplicação."""
    logger = logging.getLogger("devops")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    saida_padrao = logging.StreamHandler()
    arquivo = logging.FileHandler("aplicacao.log", encoding="utf-8")

    formatador = logging.Formatter(
        "%(name)s | %(levelname)s | %(asctime)s | %(filename)s:%(lineno)s | %(message)s"
    )

    saida_padrao.setFormatter(formatador)
    arquivo.setFormatter(formatador)

    logger.addHandler(saida_padrao)
    logger.addHandler(arquivo)

    return logger


LOGGER = configurar_logger()

LOGGER.info("Esse é um log de informação")
LOGGER.debug("Esse é um log de depuração. Não aparecerá")
LOGGER.warning("Esse é um log de aviso. Sempre aparecerá")
