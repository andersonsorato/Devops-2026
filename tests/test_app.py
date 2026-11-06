"""Testes da API de tarefas."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

from app.api import APP, criar_sessao

BANCO = create_engine("sqlite:///banco.db", connect_args={"check_same_thread": False})


@pytest.fixture(name="sessao")
def fixture_sessao():
    """Cria uma sessão isolada para cada teste."""
    SQLModel.metadata.create_all(BANCO)

    with Session(BANCO) as session:
        yield session

    SQLModel.metadata.drop_all(BANCO)


@pytest.fixture(name="cliente")
def fixture_cliente(sessao: Session):
    """Cria um cliente de teste com a sessão injetada."""

    def get_sessao():
        return sessao

    APP.dependency_overrides[criar_sessao] = get_sessao

    cliente = TestClient(APP)
    yield cliente

    APP.dependency_overrides.clear()


def test_index(cliente: TestClient):
    """Verifica a rota raiz."""
    resposta = cliente.get("/")
    assert resposta.status_code == 200
    assert resposta.json() == {"mensagem": "Olá, mundo!"}


def test_tarefas_get(cliente: TestClient):
    """Verifica que a rota de listagem retorna uma lista vazia."""
    resposta = cliente.get("/tarefas")
    assert resposta.status_code == 200
    assert resposta.json() == []


def test_tarefas_post(cliente: TestClient):
    """Verifica a criação de uma tarefa."""
    data_esperada = datetime.now().replace(microsecond=0).isoformat() + "Z"

    resposta = cliente.post("/tarefas?titulo=teste&descricao=teste")

    assert resposta.status_code == 201
    assert resposta.json() == {"mensagem": "OK"}

    resposta = cliente.get("/tarefas")
    assert resposta.json() == [
        {
            "_id": 1,
            "descricao": "teste",
            "data_criacao": data_esperada,
            "concluida": False,
            "titulo": "teste",
            "data_conclusao": None,
        }
    ]


def test_tarefas_put(cliente: TestClient):
    """Verifica a conclusão e o retorno de uma tarefa."""
    data_esperada = datetime.now().replace(microsecond=0).isoformat() + "Z"

    cliente.post("/tarefas?titulo=teste&descricao=teste")

    resposta = cliente.put("/tarefas/1")
    data_conclusao_esperada = datetime.now().replace(microsecond=0).isoformat() + "Z"
    assert resposta.json() == {"mensagem": "Tarefa atualizada"}

    resposta = cliente.put("/tarefas/0")
    assert resposta.json() == {"mensagem": "Tarefa não existe"}

    resposta = cliente.get("/tarefas/1")
    assert resposta.status_code == 200
    assert resposta.json() == {
        "_id": 1,
        "descricao": "teste",
        "data_criacao": data_esperada,
        "concluida": True,
        "titulo": "teste",
        "data_conclusao": str(data_conclusao_esperada),
    }


def test_tarefas_delete(cliente: TestClient):
    """Verifica a remoção de uma tarefa."""
    cliente.post("/tarefas?titulo=teste&descricao=teste")

    resposta = cliente.delete("/tarefas/0")
    assert resposta.json() == {"mensagem": "Tarefa não existe"}

    resposta = cliente.delete("/tarefas/1")
    assert resposta.json() == {"mensagem": "Tarefa removida"}

    resposta = cliente.get("/tarefas")
    assert resposta.json() == []


def test_autor(cliente: TestClient):
    """Verifica a rota do autor."""
    resposta = cliente.get("/autor")

    assert resposta.status_code == 200
    assert resposta.json() == {"mensagem": "Anderson Sorato Leme"}
