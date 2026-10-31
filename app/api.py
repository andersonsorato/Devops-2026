"""Aplicação para o módulo de extensão DevOps."""

import os
from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.exc import OperationalError
from sqlmodel import Session, SQLModel, create_engine, select

from .modelo import Tarefa

DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_USERNAME = os.getenv("DATABASE_USERNAME", "root")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "root")
DATABASE_ADDRESS = os.getenv("DATABASE_ADDRESS", "localhost")
DATABASE = os.getenv("DATABASE", "devops")


def montar_engine():
    """Cria o engine e faz fallback para SQLite quando o MySQL não estiver disponível."""
    if DATABASE_URL:
        if DATABASE_URL.startswith("sqlite"):
            return create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
        return create_engine(DATABASE_URL, pool_pre_ping=True)

    mysql_url = (
        f"postgresql+psycopg://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_ADDRESS}:3306/{DATABASE}"
    )
    try:
        engine = create_engine(mysql_url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        return engine
    except OperationalError:
        return create_engine("postgresql+psycopg:///./banco.db", connect_args={"check_same_thread": False})


ENGINE = montar_engine()


def criar_sessao():
    """Cria uma sessão de conexão com o banco de dados."""
    session = Session(ENGINE)
    try:
        yield session
    finally:
        session.close()


SESSAO = Annotated[Session, Depends(criar_sessao)]


async def inicializacao(_: FastAPI):
    """Função de inicialização da API."""
    SQLModel.metadata.create_all(ENGINE)
    yield


APP = FastAPI(lifespan=inicializacao)


def formatar_data(value):
    """Padroniza datetime para string ISO com timezone UTC e sem microssegundos."""
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        else:
            value = value.astimezone(timezone.utc)
        return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return value


def serializar_tarefa(tarefa: Tarefa):
    """Converte a tarefa para um dicionário JSON serializável."""
    return {
        "_id": tarefa.id,
        "titulo": tarefa.titulo,
        "descricao": tarefa.descricao,
        "concluida": tarefa.concluida,
        "data_criacao": formatar_data(tarefa.data_criacao),
        "data_conclusao": formatar_data(tarefa.data_conclusao),
    }


@APP.get("/tarefas")
async def tarefas(sessao: SESSAO):
    """Lista todas as tarefas."""
    lista_tarefas = sessao.exec(select(Tarefa)).all()
    return [serializar_tarefa(tarefa) for tarefa in lista_tarefas]


@APP.post("/tarefas", status_code=201)
async def post_tarefa(sessao: SESSAO, titulo: str, descricao: str | None = None):
    """Cria uma nova tarefa."""
    ultima_tarefa = sessao.exec(select(Tarefa.id).order_by(Tarefa.id.desc())).first()
    novo_id = 1 if ultima_tarefa is None else int(ultima_tarefa) + 1

    tarefa_nova = Tarefa(
        id=novo_id,
        titulo=titulo,
        descricao=descricao,
        data_criacao=datetime.now(timezone.utc).replace(microsecond=0),
    )

    sessao.add(tarefa_nova)
    sessao.commit()
    sessao.refresh(tarefa_nova)

    return {"mensagem": "OK"}


@APP.get("/tarefas/{id_tarefa}")
async def tarefa_especifica(sessao: SESSAO, id_tarefa: int):
    """Recupera uma tarefa específica."""
    resultado = sessao.exec(select(Tarefa).where(Tarefa.id == id_tarefa)).first()

    if resultado:
        return serializar_tarefa(resultado)

    return {"mensagem": "Tarefa não existe"}


@APP.put("/tarefas/{id_tarefa}")
async def concluir_tarefa(sessao: SESSAO, id_tarefa: int):
    """Conclui uma tarefa existente."""
    resultado = sessao.exec(select(Tarefa).where(Tarefa.id == id_tarefa)).first()

    if not resultado:
        return {"mensagem": "Tarefa não existe"}

    if resultado.concluida:
        return {"mensagem": "Tarefa já finalizada"}

    resultado.finalizar()
    sessao.add(resultado)
    sessao.commit()
    sessao.refresh(resultado)

    return {"mensagem": "Tarefa atualizada"}


@APP.delete("/tarefas/{id_tarefa}")
async def apagar_tarefa(sessao: SESSAO, id_tarefa: int):
    """Remove uma tarefa."""
    resultado = sessao.exec(select(Tarefa).where(Tarefa.id == id_tarefa)).first()

    if not resultado:
        return {"mensagem": "Tarefa não existe"}

    sessao.delete(resultado)
    sessao.commit()

    return {"mensagem": "Tarefa removida"}


@APP.get("/")
async def index():
    """Rota raiz."""
    return {"mensagem": "Olá, mundo!"}


@APP.get("/autor")
async def autor():
    """Retorna o autor da aplicação."""
    return {"mensagem": "Anderson Sorato Leme"}
