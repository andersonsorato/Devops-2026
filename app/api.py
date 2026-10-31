"""Aplicação para o módulo de extensão DevOps."""

from datetime import datetime
from typing import Optional

import requests
from fastapi import FastAPI
from requests.exceptions import ConnectionError as RequestConnectionError

from .modelo import Tarefa

APP = FastAPI()
TAREFAS = []


@APP.get("/tarefas")
async def tarefas():
    """Lista todas as tarefas com somente o id e o título."""
    lista_somente_id_titulo = []

    for tarefa in TAREFAS:
        lista_somente_id_titulo.append(tarefa.resumir())

    return lista_somente_id_titulo


@APP.post("/tarefas", status_code=201)
async def post_tarefa(titulo: str, descricao: Optional[str] = None):
    """Cria uma nova tarefa."""
    tarefa_nova = Tarefa(
        _id=len(TAREFAS),
        titulo=titulo,
        descricao=descricao,
        data_criacao=datetime.now().isoformat(timespec="seconds"),
    )

    TAREFAS.append(tarefa_nova)

    return {"mensagem": "OK"}


@APP.get("/tarefas/{id_tarefa}")
async def tarefa_especifica(id_tarefa: int):
    """Retorna uma tarefa específica."""
    for tarefa in TAREFAS:
        if id_tarefa == tarefa.get_id():
            return tarefa

    return {"mensagem": "Tarefa não existe"}


@APP.put("/tarefas/{id_tarefa}")
async def concluir_tarefa(id_tarefa: int):
    """Marca uma tarefa como concluída."""
    for tarefa in TAREFAS:
        if id_tarefa == tarefa.get_id() and not tarefa.concluida:
            tarefa.finalizar()
            titulo = tarefa.titulo

            try:
                requests.post(
                    f"http://localhost:8000/notificar?id={tarefa.get_id()}&titulo={titulo}",
                    timeout=1,
                )
            except RequestConnectionError as exc:
                print(exc)

            return {"mensagem": "Tarefa atualizada"}

    return {"mensagem": "Tarefa não existe"}


@APP.delete("/tarefas/{id_tarefa}")
async def apagar_tarefa(id_tarefa: int):
    """Remove uma tarefa pela identificação."""
    indice = 0
    for tarefa in TAREFAS:
        if id_tarefa == tarefa.get_id():
            TAREFAS.pop(indice)
            return {"mensagem": "Tarefa apagada"}

        indice += 1

    return {"mensagem": "Tarefa não existe"}


@APP.get("/")
async def index():
    """Rota raiz."""
    return {"mensagem": "Olá, mundo!"}


@APP.get("/autor")
async def autor():
    """Retorna o autor da aplicação."""
    return {"mensagem": "Anderson Sorato Leme"}
