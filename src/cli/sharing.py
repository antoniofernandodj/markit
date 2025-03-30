from src.cli.utils import run_async
from src.uow import UnityOfWork
from typer import Typer, confirm, prompt, echo
from click import Choice


app = Typer(help='Comandos para gerenciar compartilhamentos.')


@app.command()
@run_async
async def calendar(calendar_id: str):
    """Compartilha um calendário com outro usuário."""

    shared_with_email = prompt("ID do usuário com quem deseja compartilhar")
    public = confirm("Deseja tornar o compartilhamento público?")
    permissions = prompt("Permissões", type=Choice(["read", "write", "read_write"]))

    async with UnityOfWork() as uow:
        sharing = await uow.sharing_service.compartilhar_calendario(
            calendar_id=calendar_id,
            shared_with_email=shared_with_email,
            public=public,
            permissions=permissions
        )

        await uow.commit()

    echo("Calendário compartilhado com sucesso!")
    echo(sharing.to_pydantic().model_dump_json(indent=4))


@app.command()
@run_async
async def list_from_calendar(calendar_id: str):
    """Lista todos os compartilhamentos de um calendário específico."""

    async with UnityOfWork() as uow:
        sharings = await uow.sharing_service.obter_compartilhamentos_por_calendario(calendar_id)

    for sharing in sharings:
        echo(sharing.to_pydantic().model_dump_json(indent=4))


@app.command()
@run_async
async def remove(sharing_id: str):
    """Remove um compartilhamento específico pelo ID."""

    async with UnityOfWork() as uow:
        await uow.sharing_service.deletar_compartilhamento(sharing_id)

    echo("Compartilhamento removido com sucesso!")


@app.command()
@run_async
async def update(sharing_id: str):
    """Atualiza as permissões e a visibilidade de um compartilhamento existente."""

    permissions = prompt("Novas permissões", type=Choice(["read", "write", "read_write"]))
    public = confirm("Tornar público?")

    async with UnityOfWork() as uow:
        await uow.sharing_service.atualizar_compartilhamento(
            sharing_id=sharing_id,
            permissions=permissions,
            public=public
        )

    echo("Compartilhamento atualizado com sucesso!")
