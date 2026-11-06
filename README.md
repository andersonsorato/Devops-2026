# Lista de Tarefas - DevOps

## Sobre o projeto

Este projeto foi desenvolvido durante a disciplina de DevOps. A aplicação é uma API REST feita com FastAPI, que permite cadastrar, consultar, concluir e excluir tarefas.

Também foi configurada uma pipeline no GitHub Actions para executar os testes, gerar uma imagem Docker e publicá-la no Docker Hub. A aplicação está hospedada no Render.

## Como executar localmente

Primeiro, clone o repositório:

```bash
git clone https://github.com/andersonsorato/Devops-2026.git
cd Devops-2026
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Inicie a aplicação:

```bash
uvicorn main:APP --host 0.0.0.0 --port 8000 --reload
```

Depois, acesse a documentação pelo navegador:

http://localhost:8000/docs

## Tecnologias utilizadas

- Python e FastAPI para desenvolver a API.
- Pytest para executar os testes.
- pylist analisa o código Python para identificar possíveis erros e problemas de qualidade.
- Docker para criar a imagem da aplicação.
- GitHub Actions para automatizar o CI/CD.
- Docker Hub para armazenar a imagem.
- Render para hospedar a aplicação.

## Links

**API no Render:** https://api-200h.onrender.com/docs

**Imagem no Docker Hub:** https://hub.docker.com/r/andersonsorato/tarefas

**Repositório:** https://github.com/andersonsorato/Devops-2026
