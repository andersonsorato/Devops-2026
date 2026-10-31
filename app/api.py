"""Aplicação para o módulo de extensão DevOps"""

from datetime import datetime, timezone
from typing import Annotated, List

import requests
from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session, create_engine, select
from requests.exceptions import ConnectionError as RequestConnectionError

from .modelo import Tarefa

ENGINE = create_engine("sqlite:///banco.db", connect_args={'check_same_thread': False})
def criar_sessao():
    with Session(ENGINE) as s:
        yield s

SESSAO = Annotated[Session, Depends(criar_sessao)]

async def inicializacao(api: FastAPI):
    SQLModel.metadata.create_all(ENGINE)
    yield

APP = FastAPI(lifespan=inicializacao)
TAREFAS = []


# GET /tarefas: Lista todas as tarefas (somente id e titulo)
@APP.get("/tarefas")
async def tarefas(sessao: SESSAO) -> List[Tarefa]:
    """Rota para listar as tarefas."""

    lista_tarefas = sessao.exec(select(Tarefa).offset(0)).all()

    return lista_tarefas
    


# POST /tarefas: Cria tarefa
@APP.post("/tarefas", status_code=201)
async def post_tarefa(sessao: SESSAO, titulo: str, descricao: str = None):
    """Rota para criar uma tarefa."""
    tarefa_nova = Tarefa(
        titulo=titulo,
        descricao=descricao,
        data_criacao=datetime.now().astimezone(timezone.utc),
    )

    sessao.add(tarefa_nova)
    sessao.commit()
    sessao.refresh(tarefa_nova)

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
