import pytest

from fastapi.testclient import TestClient
from app.api import APP, criar_sessao
from datetime import datetime
from sqlmodel import SQLModel, Session, create_engine

DATA = None
DATA_CONCLUSAO = None
BANCO = create_engine("sqlite:///banco.db", connect_args={"check_same_thread": False})

@pytest.fixture(name="sessao")
def fixture_sessao():
    SQLModel.metadata.create_all(BANCO)

    with Session(BANCO) as s:
        yield s

    SQLModel.metadata.drop_all(BANCO)

@pytest.fixture(name='cliente')
def fixture_cliente(sessao: Session):
    def get_sessao():
        return sessao

    APP.dependency_overrides[criar_sessao] = get_sessao

    cliente = TestClient(APP)
    yield cliente

    APP.dependency_overrides.clear()

def test_index(cliente: TestClient):
    resposta = cliente.get("/")
    assert resposta.status_code == 200
    assert resposta.json() == {"mensagem": "Olá, mundo!"}


# 1. Implementar um teste unitário para a rota /tarefas (GET)
def test_tarefas_get(cliente: TestClient):
    resposta = cliente.get("/tarefas")
    assert resposta.status_code == 200

    # Testando se a rota retorna uma lista vazia
    assert resposta.json() == []


# 2. Implementar um teste unitário para a rota /tarefas (POST)
def test_tarefas_post(cliente: TestClient):
    global DATA
    resposta = cliente.post("/tarefas?titulo=teste&descricao=teste")
    DATA = datetime.now().isoformat(timespec="seconds")

    assert resposta.status_code == 201
    assert resposta.json() == {"mensagem": "OK"}

    resposta = cliente.get("/tarefas")
    assert resposta.json() == [{"0": "teste"}]


def test_tarefa_criada(cliente: TestClient):
    global DATA

    resposta = cliente.post("/tarefas?titulo=teste&descricao=teste")
    DATA = datetime.now().isoformat(timespec="seconds")

    assert resposta.status_code == 201
    assert resposta.json() == {"mensagem": "OK"}

    resposta = cliente.get("/tarefas/0")
    assert resposta.status_code == 200
    assert resposta.json() == {
        "_id": 0,
        "titulo": "teste",
        "descricao": "teste",
        "concluida": False,
        "data_criacao": str(DATA),
        "data_conclusao": None,
    }


# 3. Implementar um teste unitário para a rota /tarefas/{id} (PUT)
def test_tarefas_put(cliente: TestClient):
    global DATA_CONCLUSAO
    resposta = cliente.put("/tarefas/0")
    DATA_CONCLUSAO = datetime.now().isoformat(timespec="seconds")
    assert resposta.json() == {"mensagem": "Tarefa atualizada"} or {"mensagem": "Tarefa não existe"}

    resposta = cliente.put("/tarefas/1")
    assert resposta.json() == {"mensagem": "Tarefa não existe"}


# 4. Implementar um teste unitário para a rota /tarefas/{id} (GET)
def test_tarefas_get_id(cliente: TestClient):
    resposta = cliente.get("/tarefas/0")
    assert resposta.status_code == 200
    assert resposta.json() == {
        "_id": 0,
        "titulo": "teste",
        "descricao": "teste",
        "concluida": True,
        "data_criacao": str(DATA),
        "data_conclusao": str(DATA_CONCLUSAO),
    } or {"mensagem": "Tarefa não existe"}

    resposta = cliente.get("/tarefas/1")
    assert resposta.json() == {"mensagem": "Tarefa não existe"}


# 5. Implementar um teste unitário para a rota /tarefas/{id} (DELETE)
def test_tarefas_delete(cliente: TestClient):
    resposta = cliente.delete("/tarefas/1")
    assert resposta.json() == {"mensagem": "Tarefa não existe"}

    resposta = cliente.delete("/tarefas/0")
    assert resposta.json() == {"mensagem": "Tarefa apagada"} or {"mensagem": "Tarefa não existe"}

    resposta = cliente.get("/tarefas")
    assert resposta.json() == []


def test_autor(cliente: TestClient):
    resposta = cliente.get("/autor")

    assert resposta.status_code == 200
    assert resposta.json() == {"mensagem": "Anderson Sorato Leme"}

