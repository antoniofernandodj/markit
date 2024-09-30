from src.uow import UnityOfWork
from src.domain.models import Calendar, User
    


async def test_write():
    async with UnityOfWork() as uow:
        await uow.user_service.cadastrar_usuario(
            nome='Jane Doe',
            email="Janedoe@example.com",
            senha="password"
        )
        

    async with UnityOfWork() as uow:

        jane_doe = await uow.user_repository.find_by_email("Janedoe@example.com")

        assert jane_doe

        calendar = Calendar(
            name="Jane Doe Calendar",
            user_id=jane_doe.get_id(),
            public=True
        )
        await uow.calendar_repository.save(calendar)

    async with UnityOfWork() as uow:
        assert await uow.calendar_repository.find_by_name("Jane Doe Calendar")


async def test_update():
    async with UnityOfWork() as uow:
        calendar = await uow.calendar_repository.find_by_name("Jane Doe Calendar")
        assert calendar

        await uow.calendar_repository.update(
            calendar.get_id(), {"name": "Jane's Calendar"}
        )

    async with UnityOfWork() as uow:
        user = await uow.calendar_repository.find_by_name("Jane's Calendar")

    assert user



# async def test_delete():
#     async with UnityOfWork() as uow:
#         calendar = await uow.calendar_repository.find_by_name("John's Calendar")
#         assert calendar
#         await uow.calendar_repository.delete(calendar)

#     async with UnityOfWork() as uow:
#         user = await uow.calendar_repository.find_by_name("John Doe Calendar")
#         assert user is None
    