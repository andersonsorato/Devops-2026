"""Modelos da aplicação de tarefas."""

from datetime import datetime


class Tarefa:
    """Representa uma tarefa da aplicação."""

    def __init__(
        self,
        _id: int | None = None,
        titulo: str = "",
        descricao: str | None = None,
        concluida: bool = False,
        data_criacao: datetime | str | None = None,
        data_conclusao: str | None = None,
    ):
        self._id = _id
        self.titulo = titulo
        self.descricao = descricao
        self.concluida = concluida
        if isinstance(data_criacao, str):
            self.data_criacao = datetime.fromisoformat(data_criacao)
        else:
            self.data_criacao = (data_criacao or datetime.now()).replace(microsecond=0)
        self.data_conclusao = data_conclusao

    @property
    def id(self) -> int | None:
        """Retorna o identificador da tarefa."""
        return self._id

    @id.setter
    def id(self, value: int | None) -> None:
        """Define o identificador da tarefa."""
        self._id = value

    def finalizar(self) -> None:
        """Finaliza a tarefa atual."""
        self.concluida = True
        self.data_conclusao = datetime.now().isoformat(timespec="seconds")

    def resumir(self) -> dict[int | None, str]:
        """Resume a tarefa em um dicionário com id e título."""
        return {self.id: self.titulo}

    def to_dict(self) -> dict[str, str | bool | int | None]:
        """Serializa a tarefa como dicionário compatível com JSON."""
        data_criacao = (
            self.data_criacao.isoformat(timespec="seconds")
            if isinstance(self.data_criacao, datetime)
            else self.data_criacao
        )
        return {
            "_id": self._id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "concluida": self.concluida,
            "data_criacao": data_criacao,
            "data_conclusao": self.data_conclusao,
        }

    def get_id(self) -> int | None:
        """Retorna o id da tarefa."""
        return self._id
