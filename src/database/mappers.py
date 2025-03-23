from sqlalchemy.orm import registry


mapper_registry = registry()


def start_mappers():
    from src.domain.models import User, Calendar, Event, Sharing
    from src.database.entities import users, calendars, events, sharing
    from sqlalchemy.orm import relationship, Mapper  # noqa

    # Limpa os mapeamentos antes de recriá-los
    global mapper_registry
    mapper_registry.dispose()
    mapper_registry = registry()  # Recria o registry

    event_mapper: Mapper[Event] = mapper_registry.map_imperatively(Event, events)

    sharing_mapper: Mapper[Sharing] = mapper_registry.map_imperatively(Sharing, sharing)

    calendar_mapper: Mapper[Calendar] = mapper_registry.map_imperatively(
        Calendar,
        calendars,
        properties={
            "events": relationship(event_mapper),
            "sharing": relationship(sharing_mapper),
        },
    )

    mapper_registry.map_imperatively(
        User,
        users,
        properties={"calendars": relationship(calendar_mapper)},
    )

    return mapper_registry


def clear_mappers():
    """Remove todos os mapeamentos registrados no SQLAlchemy."""
    global mapper_registry
    mapper_registry.dispose()
    mapper_registry = registry()
