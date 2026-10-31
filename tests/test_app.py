"""Testes de integração da API."""

from datetime import datetime

from fastapi.testclient import TestClient

from app.api import APP

# pylint: disable=global-statement

CLIENT = TestClient(APP)
DATA = None
DATA_CONCLUSAO = None


def test_index():
    """Verifica a rota inicial da API."""
    resposta = CLIENT.get("/")
    assert resposta.status_code == 200
    assert resposta.json() == {"mensagem": "Olá, mundo!"}


def test_tarefas_get():
    """Verifica a listagem vazia de tarefas."""
    resposta = CLIENT.get("/tarefas")
    assert resposta.status_code == 200
    assert resposta.json() == []


def test_tarefas_post():
    """Verifica a criação de uma tarefa."""
    global DATA
    resposta = CLIENT.post("/tarefas?titulo=teste&descricao=teste")
    DATA = datetime.now().isoformat(timespec="seconds")

    assert resposta.status_code == 201
    assert resposta.json() == {"mensagem": "OK"}

    resposta = CLIENT.get("/tarefas")
    assert resposta.json() == [{"0": "teste"}]


def test_tarefa_criada():
    """Verifica a tarefa recém-criada."""
    resposta = CLIENT.get("/tarefas/0")
    assert resposta.status_code == 200
    assert resposta.json() == {
        "_id": 0,
        "titulo": "teste",
        "descricao": "teste",
        "concluida": False,
        "data_criacao": str(DATA),
        "data_conclusao": None,
    }


def test_tarefas_put():
    """Verifica a finalização de uma tarefa."""
    global DATA_CONCLUSAO
    resposta = CLIENT.put("/tarefas/0")
    DATA_CONCLUSAO = datetime.now().isoformat(timespec="seconds")
    assert resposta.json() == {"mensagem": "Tarefa atualizada"}

    resposta = CLIENT.put("/tarefas/1")
    assert resposta.json() == {"mensagem": "Tarefa não existe"}


def test_tarefas_get_id():
    """Verifica a consulta de uma tarefa concluída."""
    resposta = CLIENT.get("/tarefas/0")
    assert resposta.status_code == 200
    assert resposta.json() == {
        "_id": 0,
        "titulo": "teste",
        "descricao": "teste",
        "concluida": True,
        "data_criacao": str(DATA),
        "data_conclusao": str(DATA_CONCLUSAO),
    }

    resposta = CLIENT.get("/tarefas/1")
    assert resposta.json() == {"mensagem": "Tarefa não existe"}


def test_tarefas_delete():
    """Verifica a exclusão de uma tarefa."""
    resposta = CLIENT.delete("/tarefas/1")
    assert resposta.json() == {"mensagem": "Tarefa não existe"}

    resposta = CLIENT.delete("/tarefas/0")
    assert resposta.json() == {"mensagem": "Tarefa apagada"}

    resposta = CLIENT.get("/tarefas")
    assert resposta.json() == []


def test_autor():
    """Verifica a rota de autoria."""
    resposta = CLIENT.get("/autor")

    assert resposta.status_code == 200
    assert resposta.json() == {"mensagem": "Anderson Sorato Leme"}
