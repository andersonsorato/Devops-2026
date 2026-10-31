"""Modelos da aplicação de tarefas."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Tarefa(SQLModel, table=True):
    """Modelo de tarefa."""

    id: int | None = Field(alias="_id", primary_key=True, unique=True, default=None)
    titulo: str
    descricao: Optional[str] = None
    concluida: bool = False
    data_criacao: datetime
    data_conclusao: Optional[datetime] = None

    def __init__(self, **data):
        """Converte string de datas para o tipo datetime."""
        if "data_criacao" in data and isinstance(data["data_criacao"], str):
            data["data_criacao"] = datetime.fromisoformat(data["data_criacao"])
        if "data_conclusao" in data and isinstance(data["data_conclusao"], str):
            data["data_conclusao"] = datetime.fromisoformat(data["data_conclusao"])
        super().__init__(**data)

    def finalizar(self):
        """Método para finalizar tarefa."""
        self.concluida = True
        self.data_conclusao = (
            datetime.now().replace(tzinfo=None).isoformat(timespec="seconds")
        )

    def resumir(self):
        """Resume tarefa em `id: titulo`."""
        return {self.id: self.titulo}

    def get_id(self):
        """Retorna ID da tarefa."""
        return self.id
