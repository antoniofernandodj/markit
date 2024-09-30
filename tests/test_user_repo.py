from src.uow import UnityOfWork
from src.domain.models import User
    


async def test_write():
    async with UnityOfWork() as uow:
        await uow.user_service.cadastrar_usuario(
            nome="John Doe",
            email="johndoe@example.com",
            senha="hashed_password"
        )

    async with UnityOfWork() as uow:
        assert await uow.user_repository.find_by_email("johndoe@example.com")


async def test_update():
    async with UnityOfWork() as uow:
        user = await uow.user_repository.find_by_email("johndoe@example.com")
        assert user
        await uow.user_repository.update(
            user.get_id(), {"name": "Jane Doe"}
        )

    async with UnityOfWork() as uow:
        user = await uow.user_repository.find_by_email("johndoe@example.com")

    assert user
    assert user.name == 'Jane Doe'


async def test_delete():
    async with UnityOfWork() as uow:
        user = await uow.user_repository.find_by_email("johndoe@example.com")
        assert user
        await uow.user_repository.delete(user)

    async with UnityOfWork() as uow:
        user = await uow.user_repository.find_by_email("johndoe@example.com")
        assert user is None

async def test_delete_all():
    async with UnityOfWork() as uow:
        users = await uow.user_repository.all()
        for user in users:
            await uow.user_service.remover_usuario(user)

    async with UnityOfWork() as uow:
        users = await uow.user_repository.all()
        assert not users
