from .auth import router as auth_router
from .calendar import router as calendar_router
from .event import router as event_router
from .sharing import router as sharing_router
from .user import router as user_router


"""
Cadastrar User 1 {
    "detail": "Usuário cadastrado com sucesso!",
    "user": {
        0bf168dd-d10d-44fc-98f1-65d68ad3620a
        "name": "user1@example.com",
        "email": "user1@example.com",
        "password": "123456"
    }
}

Cadastrar User 2 {
    "detail": "Usuário cadastrado com sucesso!",
    "user": {
        0cb8b0f4-4cb9-4c0a-8a43-341b8db253f3
        "name": "user2@example.com",
        "email": "user2@example.com",
        "password": "123456"
    }
}

Cadastrar User 3 {
    "detail": "Usuário cadastrado com sucesso!",
    "user": {
        68a9730c-cf55-432a-925c-d1a63e935437
        "name": "user3@example.com",
        "email": "user3@example.com",
        "password": "123456"
    }
}

Cadastrar Calendario 1 {
    "detail": "Calendário cadastrado com sucesso",
    "calendario": {
        a46b3ad1-9d94-4326-b5a6-2c6a15bfddca
        "name": "semana",
        "user_id": "0bf168dd-d10d-44fc-98f1-65d68ad3620a"
    }
}

Cadastrar Evento 1 {
    "detail": "Evento cadastrado com sucesso!",
    "event": {
        f06cd7d2-4f90-4d73-bbab-7c4e631b5636
        "calendar_id": "a46b3ad1-9d94-4326-b5a6-2c6a15bfddca",
        "title": "event1",
        "description": "e1",
        "start_time": "2024-09-30T02:24:01.269000+00:00",
        "end_time": "2025-09-30T02:24:01.269000+00:00",
        "is_recurring": false
    }
}

Cadastrar Evento 2 {
    8837e60a-114d-4ca9-a472-302ef5b2b95d
    "calendar_id": "a46b3ad1-9d94-4326-b5a6-2c6a15bfddca",
    "title": "event2",
    "description": "e2",
    "start_time": "2024-09-30T02:24:01.269Z",
    "end_time": "2025-09-30T02:24:01.269Z",
    "is_recurring": false
}


Gerar compartilhamento para user 2 de calendario 1 {
    228cb55d-1e9f-4b3c-817b-8a3569afdccd
    "detail": "Calendário compartilhado com sucesso!",
    "sharing": {
        "calendar_id": "a46b3ad1-9d94-4326-b5a6-2c6a15bfddca",
        "shared_with_id": "0cb8b0f4-4cb9-4c0a-8a43-341b8db253f3",
        "permissions": "read",
        "public": false
    }
}

acessar calendario 1 Deslogado


acessar calendario 1 como user 1
acessar calendario 1 como user 2
acessar calendario 1 como user 3

editar evento 1 como user 1
editar evento 1 como user 2
editar evento 1 como user 3

remover evento 1 como user 1
remover evento 1 como user 2
remover evento 1 como user 3

"""