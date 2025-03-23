from datetime import datetime
from typer import Typer, confirm, prompt, echo
from typing import Optional
from src.api.schema import EventCreateRequest, EventUpdateRequest
from src.api.utils import get_logged_in_id
from src.cli.utils import run_async
from src.uow import UnityOfWork
from .utils import strip_or_none


app = Typer(help="Comandos para gerenciar eventos.")


@app.command()
@run_async
async def show(event_id: str):
    """Obter evento por ID."""

    token: Optional[str] = str(prompt("Insira o token de autenticação").strip()) or None
    sharing_code: Optional[str] = str(prompt("Insira o código de compartilhamento").strip()) or None

    async with UnityOfWork() as uow:
        event = await uow.event_service.acessar_evento_por_id(
            event_id=event_id,
            logged_in_id=await get_logged_in_id(token),
            sharing_code=sharing_code
        )

    echo(event.to_pydantic().model_dump_json(indent=4))


@app.command()
@run_async
async def create():
    """Cadastrar um novo evento."""

    calendar_id = prompt("Insira o ID do calendário")
    titulo = prompt("Insira o título do evento")
    descricao = prompt("Insira a descrição do evento")
    inicio_str = prompt("Insira a data de início do evento")
    fim_str = prompt("Insira a data de fim do evento")
    recorrente = confirm("O evento é recorrente?")

    inicio = datetime.fromisoformat(inicio_str)
    fim = datetime.fromisoformat(fim_str)

    body = EventCreateRequest(
        calendar_id=calendar_id,
        title=titulo,
        description=descricao,
        start_time=inicio,
        end_time=fim,
        is_recurring=recorrente
    )

    async with UnityOfWork() as uow:
        await uow.event_service.cadastrar_evento(
            calendar_id=body.calendar_id,
            titulo=body.title,
            descricao=body.description,
            inicio=body.start_time,
            fim=body.end_time,
            recorrente=body.is_recurring
        )

        await uow.commit()

    echo("Evento cadastrado com sucesso!")


@app.command()
@run_async
async def remove(event_id: str):
    """Deletar evento por ID."""

    token: Optional[str] = strip_or_none(prompt("Insira o token de autenticação"))
    sharing_code: Optional[str] = strip_or_none(prompt("Insira o código de compartilhamento"))

    async with UnityOfWork() as uow:
        await uow.event_service.deletar_evento(
            event_id=event_id,
            logged_in_id=await get_logged_in_id(token),
            sharing_code=sharing_code
        )

    echo("Evento removido com sucesso")


@app.command()
@run_async
async def update(event_id: str):
    """Atualizar evento por ID."""

    titulo = strip_or_none(prompt("Insira o título do evento", default=""))
    descricao = strip_or_none(prompt("Insira a descrição do evento", default=""))
    inicio_str = strip_or_none(prompt("Insira a data de início do evento", default=""))
    fim_str = strip_or_none(prompt("Insira a data de fim do evento", default=""))
    recorrente = confirm("O evento é recorrente?")

    inicio = datetime.fromisoformat(inicio_str) if inicio_str else None
    fim = datetime.fromisoformat(fim_str) if fim_str else None

    token: Optional[str] = str(prompt("Insira o token de autenticação").strip()) or None
    sharing_code: Optional[str] = str(prompt("Insira o código de compartilhamento").strip()) or None

    body = EventUpdateRequest(
        title=titulo, description=descricao, start_time=inicio, end_time=fim, is_recurring=recorrente
    )

    async with UnityOfWork() as uow:
        await uow.event_service.atualizar_evento(
            event_id=event_id,
            titulo=body.title,
            descricao=body.description,
            inicio=body.start_time,
            fim=body.end_time,
            recorrente=body.is_recurring,
            logged_in_id=await get_logged_in_id(token),
            sharing_code=sharing_code,
        )

    echo("Evento atualizado com sucesso")


@app.command()
@run_async
async def list_from_calendar(calendar_id: str):
    """Obter eventos por calendário"""

    token: Optional[str] = strip_or_none(prompt("Insira o token de autenticação", default=""))
    sharing_code = prompt("Insira o código de compartilhamento", default="")

    async with UnityOfWork() as uow:

        calendar = await uow.calendar_service.obter_calendario(
            calendar_id=calendar_id,
            logged_in_id=await get_logged_in_id(token),
            sharing_code=sharing_code
        )

        eventos = await uow.event_service.obter_eventos_por_calendario(
            calendar=calendar,
        )

        for evento in eventos:
            echo(evento.to_pydantic().model_dump_json(indent=4))
