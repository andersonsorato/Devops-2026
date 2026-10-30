"""API de tarefas para criar, listar, atualizar e remover tarefas."""

import logging
import os
from datetime import datetime

import httpx
from fastapi import FastAPI

APP = FastAPI()
TAREFAS: list[dict] = []
log = logging.getLogger("uvicorn.error")
NOTIFICACAO_URL = os.getenv("NOTIFICACAO_URL", "http://127.0.0.1:8002/notificacoes")

# Estrutura da tarefa
# {
#     "id": int,
#     "titulo": str,
#     "descricao": str,
#     "concluida": bool,
#     "criada_em": datetime,
# }


def criar_tarefa(titulo: str, descricao: str):
    """Cria uma nova tarefa com dados iniciais."""
    tarefa = {
        "id": len(TAREFAS),
        "titulo": titulo,
        "descricao": descricao,
        "concluida": False,
        "criada_em": datetime.now().replace(microsecond=0),
    }
    log.info("Tarefa criada: %s", tarefa)
    return tarefa


@APP.get("/tarefas")
async def listar_tarefas():
    """Lista todas as tarefas com apenas o id e o título."""
    lista_somente_id_titulo = []

    for tarefa in TAREFAS:
        lista_somente_id_titulo.append({tarefa["id"]: tarefa["titulo"]})

    return lista_somente_id_titulo


@APP.post("/tarefas", status_code=201)
async def post_tarefa(titulo: str, descricao: str):
    """Cria uma nova tarefa e envia notificação externa."""
    tarefa_nova = criar_tarefa(titulo, descricao)

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resposta = await client.post(
                NOTIFICACAO_URL,
                json={
                    "tarefa_id": tarefa_nova["id"],
                    "titulo": tarefa_nova["titulo"],
                    "descricao": tarefa_nova["descricao"],
                },
            )
            resposta.raise_for_status()
        log.info(
            "Notificação enviada: tarefa %s - %s",
            tarefa_nova["id"],
            tarefa_nova["titulo"],
        )
    except httpx.HTTPError as exc:
        log.warning("Notificação não enviada para %s: %s", NOTIFICACAO_URL, exc)

    TAREFAS.append(tarefa_nova)
    return {"mensagem": "OK"}


@APP.get("/tarefa/{task_id}")
async def tarefa_especifica(task_id: int):
    """Retorna uma tarefa específica pelo identificador."""
    for tarefa in TAREFAS:
        if task_id == tarefa["id"]:
            return tarefa
    return {"mensagem": "Tarefa não existe"}


@APP.put("/tarefas/{task_id}")
async def concluir_tarefa(task_id: int):
    """Marca uma tarefa como concluída e registra o horário de conclusão."""
    for tarefa in TAREFAS:
        if int(tarefa["id"]) == task_id and not tarefa["concluida"]:
            tarefa["concluida"] = True
            tarefa["concluida_em"] = datetime.now()
            return tarefa
    return {"mensagem": "Tarefa não encontrada"}


@APP.delete("/tarefas/{task_id}")
async def apagar_tarefa(task_id: int):
    """Remove uma tarefa pelo identificador."""
    for indice, tarefa in enumerate(TAREFAS):
        if int(tarefa["id"]) == task_id:
            del TAREFAS[indice]
            return {"mensagem": "Tarefa excluída com sucesso"}
    return {"mensagem": "Tarefa não encontrada"}


@APP.get("/")
async def index():
    """Endpoint inicial da API."""
    return {"mensagem": "Olá, mundo!"}
