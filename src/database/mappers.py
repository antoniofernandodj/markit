def start_mappers():

    from src.domain.models import (
        User, Calendar, Event, Sharing
    )

    from sqlalchemy.orm import registry
    from src.database.entities import (
        users, calendars, events, sharing
    )
    from sqlalchemy.orm import relationship, Mapper  # noqa

    mapper_registry = registry()

    event_mapper = mapper_registry.map_imperatively(
        Event,
        events
    )

    sharing_mapper = mapper_registry.map_imperatively(
        Sharing,
        sharing
    )

    calendar_mapper = mapper_registry.map_imperatively(
        Calendar,
        calendars,
        properties={
            "events": relationship(
                event_mapper
            ),
            "sharing": relationship(
                sharing_mapper
            )
        },
    )

    usuario_mapper = mapper_registry.map_imperatively(
        User,
        users,
        properties={
            "calendars": relationship(
                calendar_mapper
            )
        },
    )

    return mapper_registry

