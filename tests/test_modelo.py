"""Testes do modelo de tarefas."""

from datetime import datetime, timezone

from app.modelo import Tarefa


def criar_tarefa_mock():
    """Cria uma tarefa em estado inicial para testes."""
    return Tarefa(
        titulo="Tarefa teste",
        data_criacao=datetime.now().replace(microsecond=0),
    )


def test_nova_tarefa():
    """Verifica atributos iniciais da tarefa."""
    t = criar_tarefa_mock()

    assert t.get_id() is None
    assert t.titulo == "Tarefa teste"
    assert t.descricao is None
    assert t.data_criacao == datetime.now().replace(microsecond=0)
    assert t.data_conclusao is None
    assert not t.concluida


def test_tarefa_concluida():
    """Verifica a finalização de uma tarefa."""
    t = criar_tarefa_mock()

    t.finalizar()
    assert t.concluida
    assert t.data_conclusao == datetime.now().astimezone(timezone.utc).replace(microsecond=0)
