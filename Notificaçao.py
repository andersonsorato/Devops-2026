from fastapi import FastAPI
from pydantic import BaseModel

APP = FastAPI()
NOTIFICACOES = []


class Notificacao(BaseModel):
    tarefa_id: int
    titulo: str
    descricao: str

@APP.get("/")
async def tarefas():
    return {"mensagem": "Serviço de notificações ativo"}


@APP.post("/notificacoes")
async def receber_notificacao(notificacao: Notificacao):
    NOTIFICACOES.append(notificacao.model_dump())
    print(
        f"Notificação recebida: tarefa {notificacao.tarefa_id} - "
        f"{notificacao.titulo}: {notificacao.descricao}",
        flush=True,
    )
    return {"mensagem": "Notificação recebida"}


@APP.get("/notificacoes")
async def listar_notificacoes():
    return NOTIFICACOES
