from urllib import response

import httpx
from fastapi.testclient import TestClient
from app import APP, TAREFAS

client = TestClient(APP)


def reset_tarefas():
    TAREFAS.clear()


# index
def test_index():
    reset_tarefas()
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"mensagem": "Olá, mundo!"}


# get
def test_get():
    reset_tarefas()
    response = client.get("/tarefas")
    assert response.status_code == 200
    assert response.json() == []


# post
def test_post():
    reset_tarefas()
    response = client.post("/tarefas?titulo=teste&descricao=teste")
    assert response.status_code == 201
    assert response.json() == {"mensagem": "OK"}

    response = client.get("/tarefas")
    assert response.json() == [{"0": "teste"}]


# get[id]
def test_tarefa_criada():
    reset_tarefas()
    client.post("/tarefas?titulo=teste&descricao=teste")
    resposta = client.get("/tarefa/0")
    assert resposta.status_code == 200
    assert resposta.json()["id"] == 0
    assert resposta.json()["titulo"] == "teste"
    assert resposta.json()["descricao"] == "teste"
    assert resposta.json()["concluida"] is False
    assert "criada_em" in resposta.json()


def test_tarefa_nao_encontrada():
    reset_tarefas()
    response = client.get("/tarefa/99")
    assert response.status_code == 200
    assert response.json() == {"mensagem": "Tarefa não existe"}


# put[id]
def test_put_id():
    reset_tarefas()
    client.post("/tarefas?titulo=teste&descricao=teste")
    response = client.put("/tarefas/0")
    assert response.status_code == 200
    assert response.json()["concluida"] is True
    assert "concluida_em" in response.json()


def test_put_id_inexistente():
    reset_tarefas()
    response = client.put("/tarefas/999")
    assert response.status_code == 200
    assert response.json() == {"mensagem": "Tarefa não encontrada"}


# delete[id]
def test_delete_id():
    reset_tarefas()
    client.post("/tarefas?titulo=teste&descricao=teste")
    response = client.delete("/tarefas/0")
    assert response.status_code == 200
    assert response.json() == {"mensagem": "Tarefa excluída com sucesso"}


def test_delete_id_inexistente():
    reset_tarefas()
    response = client.delete("/tarefas/999")
    assert response.status_code == 200
    assert response.json() == {"mensagem": "Tarefa não encontrada"}


def test_post_sem_notificacao(monkeypatch):
    reset_tarefas()

    async def fake_post(self, *args, **kwargs):
        raise httpx.HTTPError("falha de rede")

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)
    response = client.post("/tarefas?titulo=teste&descricao=teste")
    assert response.status_code == 201
    assert response.json() == {"mensagem": "OK"}
