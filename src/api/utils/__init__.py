from contextlib import suppress
from typing import Optional
from fastapi import Request
from src.api.security.auth import ApiAuthService
from src.database.entities import AsyncSessionFactory


async def get_session():
    async with AsyncSessionFactory() as session:
        yield session


def get_token(request: Request):
    auth_header = request.headers.get('Authorization')
    
    if auth_header is None:
        return None

    try:
        token_type, token = auth_header.split(" ")
        if token_type.lower() != "bearer":
            return None
    except ValueError:
        return None

    return token

async def get_logged_in_id(token: Optional[str]) -> Optional[str]:
    auth_service = ApiAuthService()
    logged_user_id = None
    with suppress(Exception):
        logged_user_id = await auth_service.obter_usuario_pelo_token(token or '')

    return logged_user_id