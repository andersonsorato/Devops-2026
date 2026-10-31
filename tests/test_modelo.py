"""Testes para o modelo de tarefas."""

from datetime import datetime

from app.modelo import Tarefa


def criar_tarefa_mock():
    """Cria uma instância de tarefa para os testes."""
    return Tarefa(
        _id=0,
        titulo="Tarefa teste",
        data_criacao=datetime.now().isoformat(timespec="seconds"),
    )


def test_nova_tarefa():
    """Verifica que uma nova tarefa é criada corretamente."""
    tarefa = criar_tarefa_mock()

    assert tarefa.get_id() == 0
    assert tarefa.titulo == "Tarefa teste"
    assert tarefa.descricao is None
    assert tarefa.data_criacao.isoformat() == datetime.now().isoformat(
        timespec="seconds"
    )
    assert tarefa.data_conclusao is None
    assert not tarefa.concluida


def test_tarefa_concluida():
    """Verifica que a tarefa é finalizada corretamente."""
    tarefa = criar_tarefa_mock()

    tarefa.finalizar()
    assert tarefa.concluida
    assert tarefa.data_conclusao == datetime.now().isoformat(timespec="seconds")
