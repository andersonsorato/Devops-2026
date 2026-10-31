"""Aplicação para o módulo de extensão DevOps"""

from datetime import datetime, timezone
from typing import Annotated, List
import os

from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session, create_engine, select
from requests.exceptions import ConnectionError as RequestConnectionError

from .modelo import Tarefa

DATABASE_USERNAME = os.ENV.get("DATABASE_USERNAME", "root")
DATABASE_PASSWORD = os.ENV.get("DATABASE_PASSWORD", "root")
DATABASE_ADDRESS = os.ENV.get("DATABASE_ADDRESS", "localhost")
DATABASE = os.ENV.get("DATABASE")
if DATABASE is None:
    raise RequestConnectionError("Variável de ambiente DATABASE não definida")
    exit(1)
    
ENGINE = create_engine(f"mysql+pymysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_ADDRESS}:3306/{DATABASE}")
def criar_sessao():
    """Cria uma sessão de conexão com o banco de dados."""
    with Session(ENGINE) as s:
        yield s

SESSAO = Annotated[Session, Depends(criar_sessao)]
"""anotação para injetar a sessão do banco de dados nas rotas do FastAPI"""
async def inicializacao(api: FastAPI):
    """Função de inicialização da aplicação."""
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


# GET /tarefas/{id_tarefa}: Visualizar tarefa específica
@APP.get("/tarefas/{id_tarefa}")
async def tarefa_especifica(sessao: SESSAO, id_tarefa: int) -> Tarefa:
    """Rota para visualizar uma tarefa específica"""
    # select * from tarefas where id == id_tarefa
    regra = select(Tarefa).where(Tarefa.id == id_tarefa)
    resultado = sessao.exec(regra).all()

    if resultado:
        return resultado[0]

    return {"mensagem": "Tarefa não existe"}

# PUT /tarefas/{id}: Atualiza tarefa específica
@APP.put("/tarefas/{id_tarefa}")
async def concluir_tarefa(sessao: SESSAO, id_tarefa: int):
    """Rota para concluir uma tarefa."""

    regra = select(Tarefa).where(Tarefa.id == id_tarefa)
    resultado = sessao.exec(regra).all()

    if not resultado:
        return {"mensagem": "Tarefa não existe"}

    if resultado[0].concluida is True:
        return {"mensagem": "Tarefa já finalizada"}

    resultado[0].finalizar()

    sessao.add(resultado[0])
    sessao.commit()
    sessao.refresh(resultado[0])

    return {"mensagem": "Tarefa atualizada"}


@APP.delete("/tarefas/{id_tarefa}")
async def apagar_tarefa(sessao: SESSAO, id_tarefa: int):
    """Remove uma tarefa pela identificação."""
    selecao = select(Tarefa).where(Tarefa.id == id_tarefa)
    resultado = sessao.exec(selecao).all()

    if not resultado:
        return {"mensagem": "Tarefa não existe"}

    sessao.delete(resultado[0])
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
