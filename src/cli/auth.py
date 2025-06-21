from typer import Typer, prompt, echo, Exit
from src.api.schema import UserResponse
from src.api.security.auth import ApiAuthService
from src.cli.utils import run_async
from src.uow import UnityOfWork


app = Typer(help='Comandos para gerenciar autenticação.')


@app.command()
@run_async
async def login():
    """Autentica um usuário e retorna um token de acesso."""
    email = prompt("Email")
    password = prompt("Senha", hide_input=True)

    async with UnityOfWork() as uow:
        user = await uow.user_service.repo.find_by_email(email)

    if not user or not ApiAuthService.autenticar_usuario(user, password):
        echo("Credenciais incorretas", err=True)
        raise Exit(code=1)

    access_token = ApiAuthService.criar_token_acesso(user.get_id())
    echo(f"Token de acesso:\n{access_token}")


@app.command()
@run_async
async def ler_meus_dados():
    """Retorna os dados do usuário autenticado."""

    token = prompt("Token de acesso")
    user_id = await ApiAuthService.obter_usuario_pelo_token(token)

    async with UnityOfWork() as uow:
        user = await uow.user_service.repo.get(user_id)

    echo(UserResponse.model_validate(user).model_dump_json(indent=4))
