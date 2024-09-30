from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.schema import UserResponse
from src.api.security.auth import ApiAuthService
from src.api.utils import get_session
from src.domain.models import User
from src.domain.services import (
    CalendarService,
    EventService,
    SharingService,
    UserService
)
from src.uow import UnityOfWork



def user_service_callback(session: AsyncSession = Depends(get_session)):
    return UserService(session)


def event_service_callback(session: AsyncSession = Depends(get_session)):
    return EventService(session)


def calendar_service_callback(session: AsyncSession = Depends(get_session)):
    return CalendarService(session)


def sharing_service_callback(session: AsyncSession = Depends(get_session)):
    return SharingService(session)


def form_data_callback(
    data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm)
):
    return data

async def uow_callback():
    async with UnityOfWork() as uow:
        yield uow

user_service = Depends(user_service_callback)

async def current_user_callback(
    user_service: UserService = user_service,
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="login")),
):
    auth_service = ApiAuthService()
    user_id = await auth_service.obter_usuario_pelo_token(token)

    user = await user_service.repo.get(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )
    
    return user


uow: UnityOfWork = Depends(uow_callback)
form_data = Depends(form_data_callback)
event_service = Depends(event_service_callback)
calendar_service = Depends(calendar_service_callback)
sharing_service = Depends(sharing_service_callback)
current_user: User = Depends(current_user_callback)