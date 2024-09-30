from src.uow import UnityOfWork
from src.domain.models import Calendar, User
    


async def test_user_auth():
    async with UnityOfWork() as uow:
        await uow.user_service.cadastrar_usuario(
            nome='Sponge Bob',
            email="spongebob@example.com",
            senha="spongebobpassword"
        )

    async with UnityOfWork() as uow:

        sponge_bob = await uow.user_repository.find_by_email("spongebob@example.com")

        assert sponge_bob

        authentic =  uow.auth_service.autenticar_usuario(
            sponge_bob,
            "spongebobpassword"
        )

        assert authentic

        authentic =  uow.auth_service.autenticar_usuario(
            sponge_bob,
            "incorrectspongebobpassword"
        )

        assert not authentic

