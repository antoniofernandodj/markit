from typer import Typer, confirm, prompt, echo
from src.api.schema import UserCreateRequest, UserResponse, UserUpdateRequest
from src.cli.utils import run_async
from src.uow import UnityOfWork


app = Typer(help="Comandos para gerenciar usuários.")


@app.command()
@run_async
async def create():
    """Cadastra um novo usuário."""
    nome = prompt("Nome")
    email = prompt("Email")
    senha = prompt("Senha", hide_input=True, confirmation_prompt=True)

    confirmacao = confirm(f"Confirmar cadastro de {nome} ({email})?")
    if not confirmacao:
        echo("Cadastro cancelado.")
        return

    body = UserCreateRequest(name=nome, email=email, password=senha)

    async with UnityOfWork() as uow:
        user = await uow.user_service.cadastrar_usuario(
            nome=body.name,
            email=body.email,
            senha=body.password
        )

        await uow.commit()
        await uow.refresh([user])

    echo(f"Usuário {body.name} cadastrado com sucesso!")
    echo(f"ID: {user.get_id()}")


@app.command()
@run_async
async def remove(user_id: str):
    """Remove um usuário pelo ID."""

    confirmacao = confirm(f"Confirmar remoção do usuário {user_id}?")
    if not confirmacao:
        echo("Remoção cancelada.")
        return

    async with UnityOfWork() as uow:
        user = await uow.user_service.repo.get(user_id)
        if not user:
            echo("Usuário não encontrado.", err=True)
            return

        await uow.user_service.remover_usuario(user)
        await uow.commit()

    echo("Usuário removido com sucesso!")


@app.command()
@run_async
async def update(user_id: str):
    """Atualiza os dados de um usuário pelo ID."""

    nome = prompt("Novo nome", default="", show_default=False)
    email = prompt("Novo email", default="", show_default=False)
    senha = prompt("Nova senha", hide_input=True, confirmation_prompt=True, default="", show_default=False)

    confirmacao = confirm(f"Confirmar atualização do usuário {user_id}?")
    if not confirmacao:
        echo("Atualização cancelada.")
        return

    body = UserUpdateRequest(name=nome, email=email, password=senha)

    async with UnityOfWork() as uow:
        await uow.user_service.atualizar_dados_de_usuario(
            user_id=user_id, nome=body.name, email=body.email, senha=body.password
        )
        echo("Dados do usuário atualizados com sucesso!")


@app.command()
@run_async
async def list_all():
    """Lista todos os usuários cadastrados."""
    async with UnityOfWork() as uow:
        usuarios = await uow.user_service.repo.all()

        if not usuarios:
            echo("Nenhum usuário cadastrado.", err=True)
            return

        for usuario in usuarios:
            echo(UserResponse.model_validate(usuario).model_dump_json(indent=4))
