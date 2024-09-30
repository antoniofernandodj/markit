from src.uow import UnityOfWork
from src.domain.models import Calendar, User, Sharing, Permission
    


async def test_write():
    async with UnityOfWork() as uow:
        await uow.user_service.cadastrar_usuario(
            nome="Joane Doe",
            email="joanedoe@example.com",
            senha="hashed_password"
        )
        

    async with UnityOfWork() as uow:

        joane_doe = await uow.user_repository.find_by_email("joanedoe@example.com")
        assert joane_doe

        calendar = Calendar(
            name="Joane Doe Calendar",
            user_id=joane_doe.get_id(),
            public=True
        )
        await uow.calendar_repository.save(calendar)

    async with UnityOfWork() as uow:
        calendar = await uow.calendar_repository.find_by_name("Joane Doe Calendar")
        assert calendar

        sharing = Sharing(
            calendar_id=calendar.get_id(),
            shared_with_id=joane_doe.get_id(),
            permissions=Permission.read.value,
            public=True
        )

        await uow.sharing_repository.save(sharing)

    async with UnityOfWork() as uow:
        calendar = await uow.calendar_repository.find_by_name("Joane Doe Calendar")
        assert calendar

        sharings = await uow.sharing_repository.find_all_by_calendar(calendar)

        assert len(sharings) == 1
        


async def test_update():
    async with UnityOfWork() as uow:

        calendar = await uow.calendar_repository.find_by_name("Joane Doe Calendar")
        assert calendar

        sharings = await uow.sharing_repository.find_all_by_calendar(calendar)

        sharing = sharings[0]

        await uow.sharing_repository.update(
            sharing.get_id(), {"permissions": Permission.read_write.value}
        )

    async with UnityOfWork() as uow:
        updated_sharing = await uow.sharing_repository.get(sharing.get_id())

        assert updated_sharing

        assert updated_sharing.permissions == Permission.read_write



async def test_delete():
    async with UnityOfWork() as uow:

        calendar = await uow.calendar_repository.find_by_name("Joane Doe Calendar")
        assert calendar

        sharings = await uow.sharing_repository.find_all_by_calendar(calendar)

        sharing = sharings[0]
        await uow.sharing_repository.delete(sharing)


    async with UnityOfWork() as uow:

        calendar = await uow.calendar_repository.find_by_name("Joane Doe Calendar")
        assert calendar

        sharings = await uow.sharing_repository.find_all_by_calendar(calendar)

        assert not sharings


# async def test_delete_users():
#     async with UnityOfWork() as uow:        

#         if joane := await uow.user_repository.find_by_email("joanedoe@example.com"):
#             calendars = await uow.calendar_repository.find_all_by_user(joane.get_id())

#             for calendar in calendars:
#                 await uow.calendar_repository.delete(calendar)

#             await uow.user_repository.delete(joane)

#         if jane1 := await uow.user_repository.find_by_email("jane@example.com"):
#             calendars = await uow.calendar_repository.find_all_by_user(jane1.get_id())
#             for calendar in calendars:
#                 await uow.calendar_repository.delete(calendar)

#             await uow.user_repository.delete(jane1)

#         if jane2 := await uow.user_repository.find_by_email("Janedoe@example.com"):
#             calendars = await uow.calendar_repository.find_all_by_user(jane2.get_id())
#             for calendar in calendars:
#                 await uow.calendar_repository.delete(calendar)

#             await uow.user_repository.delete(jane2)