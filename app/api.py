"""Aplicação para o módulo de extensão DevOps."""

from datetime import datetime, timezone
from typing import Annotated
import os

from fastapi import Depends, FastAPI
from sqlmodel import Session, SQLModel, create_engine, select

from .modelo import Tarefa

DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("DATABASE")
if DATABASE_URL and DATABASE_URL.startswith("sqlite"):
    ENGINE = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
elif DATABASE_URL:
    ENGINE = create_engine(DATABASE_URL)
else:
    ENGINE = create_engine("sqlite:///./banco.db", connect_args={"check_same_thread": False})

SQLModel.metadata.create_all(ENGINE)


def criar_sessao():
    """Cria uma sessão de conexão com o banco de dados."""
    session = Session(ENGINE)
    try:
        yield session
    finally:
        session.close()


SESSAO = Annotated[Session, Depends(criar_sessao)]
"""anotação para injetar a sessão do banco de dados nas rotas do FastAPI"""


async def inicializacao(api: FastAPI):
    """Função de inicialização da aplicação."""
    SQLModel.metadata.create_all(ENGINE)
    yield


APP = FastAPI(lifespan=inicializacao)


def serializar_tarefa(tarefa: Tarefa):
    """Converte dados de tarefa para o formato esperado pelos testes."""
    data_criacao = tarefa.data_criacao
    if isinstance(data_criacao, datetime):
        data_criacao = data_criacao.astimezone(timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds")

    data_conclusao = tarefa.data_conclusao
    if isinstance(data_conclusao, datetime):
        data_conclusao = data_conclusao.astimezone(timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds")

    return {
        "_id": tarefa.id,
        "titulo": tarefa.titulo,
        "descricao": tarefa.descricao,
        "concluida": tarefa.concluida,
        "data_criacao": data_criacao,
        "data_conclusao": data_conclusao,
    }


# GET /tarefas: Lista todas as tarefas (somente id e titulo)
@APP.get("/tarefas")
async def tarefas(sessao: SESSAO):
    """Rota para listar as tarefas."""
    lista_tarefas = sessao.exec(select(Tarefa)).all()
    return [tarefa.resumir() for tarefa in lista_tarefas]


# POST /tarefas: Cria tarefa
@APP.post("/tarefas", status_code=201)
async def post_tarefa(sessao: SESSAO, titulo: str, descricao: str | None = None):
    """Rota para criar uma tarefa."""
    proximo_id = sessao.exec(select(Tarefa.id).order_by(Tarefa.id.desc())).first()
    tarefa_id = 0 if proximo_id is None else int(proximo_id) + 1
    tarefa_nova = Tarefa(
        id=tarefa_id,
        titulo=titulo,
        descricao=descricao,
        data_criacao=datetime.now(timezone.utc).replace(microsecond=0),
    )

    sessao.add(tarefa_nova)
    sessao.commit()
    sessao.refresh(tarefa_nova)

    return {"mensagem": "OK"}


# GET /tarefas/{id_tarefa}: Visualizar tarefa específica
@APP.get("/tarefas/{id_tarefa}")
async def tarefa_especifica(sessao: SESSAO, id_tarefa: int):
    """Rota para visualizar uma tarefa específica"""
    resultado = sessao.exec(select(Tarefa).where(Tarefa.id == id_tarefa)).first()

    if resultado:
        return serializar_tarefa(resultado)

    return {"mensagem": "Tarefa não existe"}


# PUT /tarefas/{id}: Atualiza tarefa específica
@APP.put("/tarefas/{id_tarefa}")
async def concluir_tarefa(sessao: SESSAO, id_tarefa: int):
    """Rota para concluir uma tarefa."""
    resultado = sessao.exec(select(Tarefa).where(Tarefa.id == id_tarefa)).first()

    if not resultado:
        return {"mensagem": "Tarefa não existe"}

    if resultado.concluida is True:
        return {"mensagem": "Tarefa já finalizada"}

    resultado.finalizar()
    if isinstance(resultado.data_conclusao, str):
        resultado.data_conclusao = datetime.fromisoformat(resultado.data_conclusao).replace(tzinfo=timezone.utc)

    sessao.add(resultado)
    sessao.commit()
    sessao.refresh(resultado)

    return {"mensagem": "Tarefa atualizada"}


@APP.delete("/tarefas/{id_tarefa}")
async def apagar_tarefa(sessao: SESSAO, id_tarefa: int):
    """Remove uma tarefa pela identificação."""
    resultado = sessao.exec(select(Tarefa).where(Tarefa.id == id_tarefa)).first()

    if not resultado:
        return {"mensagem": "Tarefa não existe"}

    sessao.delete(resultado)
    sessao.commit()

    return {"mensagem": "Tarefa apagada"}


@APP.get("/")
async def index():
    """Rota raiz."""
    return {"mensagem": "Olá, mundo!"}


@APP.get("/autor")
async def autor():
    """Retorna o autor da aplicação."""
    return {"mensagem": "Anderson Sorato Leme"}


app = APP
