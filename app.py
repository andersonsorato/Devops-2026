from fastapi import FastAPI, HTTPException
from datetime import datetime
import logging

import httpx

APP = FastAPI()
TAREFAS = []
log = logging.getLogger("uvicorn.error")

# Estrutura da tarefa
"""
{
    "id" -> int,
    "titulo" -> str,
    "descricao" -> str,
    "concluida" -> bool,
    "criada_em" -> datetime
}
"""

def criar_tarefa(titulo, descricao):
    tarefa = {
        "id": len(TAREFAS),
        "titulo": titulo,
        "descricao": descricao,
        "concluida": False,
        "criada_em": datetime.now()
    }
    console_log = f"Tarefa criada: {tarefa}"
    log.info(console_log)
    return tarefa

@APP.get("/tarefas")
async def tarefas():
    lista_somente_id_titulo = []

    for tarefa in TAREFAS:
        id_tarefa = tarefa['id']
        titulo_tarefa = tarefa['titulo']

        lista_somente_id_titulo.append({id_tarefa: titulo_tarefa})

    return lista_somente_id_titulo

@APP.post("/tarefas")
async def post_tarefa(titulo: str, descricao: str):
    global TAREFAS

    tarefa_nova = criar_tarefa(titulo, descricao)

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resposta = await client.post(
                "http://localhost:8000/notificacoes",
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
        log.exception("Falha ao enviar notificação da tarefa")
        raise HTTPException(
            status_code=502,
            detail="Não foi possível enviar a notificação para o serviço na porta 8002",
        ) from exc

    TAREFAS.append(tarefa_nova)

    return {"mensagem": "OK"}

# GET /tarefas: Lista todas as tarefas (somente id e titulo)
# GET /tarefas/{id}: Visualizar tarefa específica
# POST /tarefas: Cria tarefa
# PUT /tarefas/{id}: Atualiza tarefa específica
# DELETE /tarefas/{id}: Exclui tarefa

@APP.get("/tarefa/{id}")

async def tarefa_especifica(id: int):
    for tarefa in TAREFAS:
        if id == tarefa["id"]:
            return tarefa
    return {"mensagem": "Tarefa não existe"}
     

# PUT /tarefas/{id}: Atualiza tarefa específica
@APP.put("/tarefas/{id}")
async def concluir_tarefa(id: int):
    # 1. Selecionar a tarefa de ID recebido como parâmetro
    # 2. Marcar a tarefa como concluída
    # 3. Você deve armazenar o horário de conclusão da tarefa
    # 4. Caso a tarefa não exista, você tem que mostrar que a tarefa não existe
    
     for tarefa in TAREFAS:
                if int(tarefa["id"]) == id and tarefa["concluida"] == False:                        
                    tarefa["concluida"] = True
                    tarefa["concluida_em"] = datetime.now()                    
                    return tarefa
     return {"mensagem": "Tarefa não encontrada"}

# DELETE /tarefas/{id}: Exclui tarefa
@APP.delete("/tarefas/{id}")
async def apagar_tarefa(id: int):
    # 1. Selecionar a tarefa de ID recebido como parâmetro
    # 2. Remover tarefa da lista de tarefas
    # 3. Caso a tarefa não exista, você tem que mostrar que a tarefa não existe
    for i, tarefa in enumerate(TAREFAS):
        if int(tarefa["id"]) == id:
            del TAREFAS[i]
            return {"mensagem": "Tarefa excluída com sucesso"}
    return {"mensagem": "Tarefa não encontrada"}

@APP.get("/")
async def index():
    return {"mensagem": "Olá, mundo!"}