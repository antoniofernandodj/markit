from datetime import datetime
from src.uow import UnityOfWork
from src.domain.models import Calendar, User, Event

    


async def test_write():
    async with UnityOfWork() as uow:
        await uow.user_service.cadastrar_usuario(
            nome="Richard Smith",
            email="richardsmith@example.com",
            senha="password"
        )
        

    async with UnityOfWork() as uow:

        joane_doe = await uow.user_repository.find_by_email("richardsmith@example.com")
        assert joane_doe

        calendar = Calendar(
            name="Richard Smith",
            user_id=joane_doe.get_id(),
            public=True
        )
        await uow.calendar_repository.save(calendar)

    async with UnityOfWork() as uow:
        calendar = await uow.calendar_repository.find_by_name("Richard Smith")
        assert calendar

        event = Event(
            calendar_id=calendar.get_id(),
            title='example',
            description='desc',
            start_time=datetime(1,1,1),
            end_time=datetime(2,2,2),
            is_recurring=True
        )

        await uow.event_repository.save(event)

    async with UnityOfWork() as uow:
        calendar = await uow.calendar_repository.find_by_name("Richard Smith")
        assert calendar

        assert calendar.events

        assert len(calendar.events) == 1
        


async def test_update():
    async with UnityOfWork() as uow:

        calendar = await uow.calendar_repository.find_by_name("Richard Smith")
        assert calendar

        event = await uow.event_repository.find_by_title('example')

        assert event

        await uow.event_repository.update(
            event.get_id(), {"description": 'desc2'}
        )

    async with UnityOfWork() as uow:
        event = await uow.event_repository.find_by_title('example')

        assert event

        assert event.description == 'desc2'



async def test_delete():
    async with UnityOfWork() as uow:
        calendar = await uow.calendar_repository.find_by_name("Richard Smith")
        assert calendar

        events = await uow.event_repository.find_all_by_calendar(calendar)

        event = events[0]
        await uow.event_repository.delete(event)


    async with UnityOfWork() as uow:

        calendar = await uow.calendar_repository.find_by_name("Richard Smith")
        assert calendar

        sharings = await uow.sharing_repository.find_all_by_calendar(calendar)

        assert not sharings
