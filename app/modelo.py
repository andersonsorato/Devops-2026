"""Modelos da aplicação de tarefas."""

from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field

class Tarefa(SQLModel, table=True):
    """Modelo de tarefa."""

    id: int | None = Field(alias="_id", primary_key=True, unique=True, default=None)
    titulo: str    
    descricao: Optional[str] = None
    concluida: bool = False
    data_criacao: datetime
    data_conclusao: Optional[datetime] = None

    def finalizar(self):
        """Finaliza a tarefa atual."""
        self.concluida = True
        self.data_conclusao = datetime.now().isoformat(timespec="seconds")

    def resumir(self):
        """Resume a tarefa em um dicionário com id e título."""
        return {self.id: self.titulo}

    def get_id(self):
        """Retorna o id da tarefa."""
        return self.id
