from typer import Typer, prompt, echo, confirm
from typing import Optional
from src.api.utils import get_logged_in_id
from src.cli.utils import run_async
from src.uow import UnityOfWork
from .utils import strip_or_none

app = Typer(help="Comandos para gerenciar calendários")


@app.command()
@run_async
async def create():
    """Cadastrar um novo calendário"""

    nome = prompt("Nome do calendário")
    publico = confirm("Calendário público?")
    token = prompt("Token de acesso")

    user_id = await get_logged_in_id(token)
    if user_id is None:
        echo("Token inválido")
        return

    echo("Cadastrando calendário...")

    async with UnityOfWork() as uow:
        user = await uow.user_service.repo.get(user_id)

        await uow.calendar_service.cadastrar_calendario(
            nome=nome, public=publico, user_id=user.get_id()
        )

        await uow.commit()

    echo("Calendário cadastrado com sucesso!")


@app.command()
@run_async
async def show(calendar_id: str, eventos_recorrentes: Optional[bool] = None):
    """Obter um calendário por ID"""
    echo(f"Buscando calendário {calendar_id}...")

    token = strip_or_none(prompt("Digite o token de autenticação", default=""))
    sharing_code = strip_or_none(prompt("Digite o código de compartilhamento", default=""))

    async with UnityOfWork() as uow:
        token = None  # Não há request no CLI, então não há token
        logged_in_id = await get_logged_in_id(token)
        calendar = await uow.calendar_service.obter_calendario(
            calendar_id=calendar_id,
            logged_in_id=logged_in_id,
            sharing_code=sharing_code,
        )
        echo(calendar.to_pydantic(eventos_recorrentes).model_dump_json(indent=4))


@app.command()
@run_async
async def list_from_user():
    """Listar calendários do usuário logado"""

    token = strip_or_none(prompt("Digite o token de autenticação"))

    async with UnityOfWork() as uow:
        logged_in_id = await get_logged_in_id(token)
        if not logged_in_id:
            echo("Token inválido")
            return

        calendars = await uow.calendar_service.obter_calendarios_por_usuario(
            logged_in_id
        )

    for calendar in calendars:
        echo(calendar.to_pydantic().model_dump_json(indent=4))


@app.command()
@run_async
async def remove(calendar_id: str):
    """Deletar um calendário por ID"""

    token = strip_or_none(prompt("Digite o token de autenticação"))
    echo(f"Removendo calendário {calendar_id}...")

    async with UnityOfWork() as uow:
        await uow.calendar_service.deletar_calendario(
            calendar_id=calendar_id,
            logged_in_id=await get_logged_in_id(token),
            sharing_code=None
        )

        await uow.commit()

    echo("Calendário removido com sucesso!")


@app.command()
@run_async
async def update(calendar_id: str):
    """Atualizar um calendário por ID"""

    name = prompt("Digite o nome do calendário")

    while True:
        public_str: str = prompt("Calendário público? [y/N]", default="")
        if public_str.lower() == "y":
            public = True
            break
        elif public_str.lower() == "n":
            public = False
            break
        elif public_str.lower() == "":
            public = None
            break
        else:
            echo("Opção inválida")

    token = strip_or_none(prompt("Digite o token de autenticação", default=""))
    sharing_code = strip_or_none(prompt("Digite o código de compartilhamento", default=""))

    echo(f"Atualizando calendário {calendar_id}...")

    async with UnityOfWork() as uow:
        await uow.calendar_service.atualizar_calendario(
            calendar_id=calendar_id,
            name=name,
            sharing_code=sharing_code,
            public=public,
            logged_in_id=await get_logged_in_id(token)
        )
        await uow.commit()

    echo("Calendário atualizado com sucesso!")
