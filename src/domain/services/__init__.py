from datetime import datetime
from typing import Optional, Sequence
import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models import Calendar, Event, Sharing, User
from src.repositories import EventRepository, SharingRepository, UserRepository, CalendarRepository



class AuthService:
    def autenticar_usuario(self, user: User, senha: str) -> bool:
        return bcrypt.checkpw(
            senha.encode('utf-8'),
            user.password_hash.encode('utf-8')
        )

    def generate_hash(self, string) -> str:
        return (
            bcrypt
            .hashpw(string.encode('utf-8'), bcrypt.gensalt())
            .decode('utf-8')
        )


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(self.session)
        self.calendar_repository = CalendarRepository(self.session)
        self.events_repository = EventRepository(self.session)
        self.auth_service = AuthService()

    async def remover_usuario(self, user: User) -> None:
        calendars = await self.calendar_repository.find_all_by_user(user.get_id())
        for calendar in calendars:
            events = await self.events_repository.find_all_by_calendar(calendar)
            for event in events:

                await self.events_repository.delete(event)
            await self.calendar_repository.delete(calendar)
        await self.repo.delete(user)

    async def cadastrar_usuario(
        self,
        nome: str,
        email: str,
        senha: str
    ) -> None:

        existing_user = await self.repo.find_by_email(email)
        if existing_user:
            raise ValueError("Email já cadastrado")

        hashed = self.auth_service.generate_hash(senha)
        user = User(nome, email, hashed)
        await self.repo.save(user)

    async def atualizar_dados_de_usuario(
        self,
        user_id: str,
        nome: Optional[str] = None,
        email: Optional[str] = None,
        senha: Optional[str] = None
    ) -> None:

        user = await self.repo.get(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")

        if email:
            existing_user = await self.repo.find_by_email(email)
            if existing_user and existing_user.get_id() != user_id:
                raise ValueError("Email já cadastrado por outro usuário")
        
        password_hash = None
        if senha:
            password_hash = self.auth_service.generate_hash(senha)

        dados = {
            'name': nome,
            'email': email,
            'password_hash': password_hash
        }

        for key in list(dados.keys()):
            if dados.get(key) is None:
                dados.pop(key, None)

        await self.repo.update(user_id, dados)


class CalendarService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CalendarRepository(self.session)
        self.events_service = EventService(self.session)
        self.user_service = UserService(self.session)

    async def cadastrar_calendario(self, nome: str, public: bool, user: User):
        calendar = Calendar(nome, user.get_id(), public=public)
        await self.repo.save(calendar)
        return calendar

    async def obter_calendarios_por_usuario(self, user_id: str):
        return await self.repo.find_all_by_user(user_id)

    async def atualizar_calendario(self, calendar_id: str, name: str):
        await self.repo.update(calendar_id, {'name': name})

    async def deletar_calendario(self, calendar: Calendar):
        events = await self.events_service.obter_eventos_por_calendario(calendar)
        for event in events:
            await self.events_service.deletar_evento(event)

        await self.repo.delete(calendar)

    async def buscar_por_nome(self, nome: str) -> Optional[Calendar]:
        return await self.repo.find_by_name(nome)
    

    async def obter_permissao_de_calendario(
        self,
        logged_user_id: Optional[str],
        sharing_code: Optional[str],
        calendar_id: str,
        permission_type: str
    ):

        calendar = await self.repo.get(calendar_id)
        if calendar is None:
            print('Calendario não encontrado')
            return False

        if calendar.public:
            print('Calendario publico')
            return True

        if calendar.user_id == logged_user_id:
            print('Calendario proprio do user logado')
            return True

        sharing_repository = SharingRepository(self.session)
        if sharing_code is None:
            print('Nenhum codigo de compartilhamento encontrado')
            return False
        
        sharing = await sharing_repository.get(sharing_code)
        if sharing is None:
            print('Nenhum compartilhamento encontrado')
            return False
        
        if sharing.public:
            print('Compartilhamento publico')
            return True
        
        if permission_type not in sharing.get_permissions():
            print('Operação não permitida')
            return False

        return (
            sharing.shared_with_id == logged_user_id
        )


class EventService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = EventRepository(self.session)
        self.user_service = UserService(self.session)

    async def cadastrar_evento(
        self, 
        calendar: Calendar, 
        titulo: str, 
        descricao: Optional[str], 
        inicio: datetime, 
        fim: datetime, 
        recorrente: Optional[bool] = False
    ):

        event = Event(
            calendar_id=calendar.get_id(),
            title=titulo,
            description=descricao,
            start_time=inicio,
            end_time=fim,
            is_recurring=recorrente
        )
        await self.repo.save(event)
        return event

    async def obter_eventos_por_calendario(self, calendar: Calendar):
        return await self.repo.find_all_by_calendar(calendar)

    async def atualizar_evento(
        self,
        event_id: Optional[str],
        titulo: Optional[str],
        descricao: Optional[str],
        inicio: Optional[datetime],
        fim: Optional[datetime],
        recorrente: Optional[bool]
    ):
        
        event_data = {
            'title': titulo,
            'description': descricao,
            'start_time': inicio,
            'end_time': fim,
            'is_recurring': recorrente
        }

        for key in list(event_data.keys()):
            if event_data.get(key) is None:
                event_data.pop(key, None)

        await self.repo.update(event_id, event_data)

    async def deletar_evento(self, event: Event):
        await self.repo.delete(event)

    async def buscar_por_titulo(self, titulo: str) -> Optional[Event]:
        return await self.repo.find_by_title(titulo)

    async def obter_permissao_de_evento(
        self,
        logged_user_id: Optional[str],
        sharing_code: Optional[str],
        event_id: str,
        permission_type: str
    ):
        
        event = await self.repo.get(event_id)
        if event is None:
            return False
        
        calendar_repository = CalendarRepository(self.session)
        calendar = await calendar_repository.get(event.calendar_id)

        if calendar is None:
            print('Nenhum calendario encontrado')
            return False

        if calendar.public:
            print('Calendario publico')
            return True

        sharing_repository = SharingRepository(self.session)
        if sharing_code is None:
            print('Nenhum codigo de compartilhamento encontrado')
            return False

        sharing = await sharing_repository.get(sharing_code)
        if sharing is None:
            print('Nenhum compartilhamento encontrado')
            return False

        if sharing.public:
            print('Compartilhamento publico')
            return True
        
        if permission_type not in sharing.get_permissions():
            print('Operação não permitida')
            return False

        return (
            sharing.shared_with_id == logged_user_id and
            sharing.calendar_id == event.calendar_id
        )


class SharingService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SharingRepository(self.session)

    async def compartilhar_calendario(
        self, 
        calendar: Calendar, 
        shared_with: User,
        public: bool,
        permissions: str
    ):
        sharing = Sharing(
            calendar_id=calendar.get_id(),
            shared_with_id=shared_with.get_id(),
            permissions=permissions,
            public=public
        )
        await self.repo.save(sharing)
        return sharing

    async def obter_compartilhamentos_por_calendario(
        self,
        calendar: Calendar
    ) -> Sequence[Sharing]:

        return await self.repo.find_all_by_calendar(calendar)

    async def atualizar_compartilhamento(
        self,
        sharing_id: str,
        permissions: str,
        public: bool
    ):
        await self.repo.update(sharing_id, {
            "permissions": permissions,
            "public": public
        })

    async def deletar_compartilhamento(self, sharing: Sharing):
        await self.repo.delete(sharing)
