from datetime import timedelta
from passlib.context import CryptContext
from jose import JWTError
from fastapi import HTTPException

from src.api.security.jwt import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    criar_token_acesso,
    verificar_token_acesso
)

from src.domain.models import User
from src.domain.services import AuthService

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class ApiAuthService:

    @classmethod
    def autenticar_usuario(cls, usuario: User, senha: str) -> bool:
        auth_service = AuthService()
        return auth_service.autenticar_usuario(usuario, senha)

    @classmethod
    def criar_token_acesso(cls, user_id: str):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        return criar_token_acesso({"sub": user_id}, expires_delta=access_token_expires)

    @classmethod
    async def obter_usuario_pelo_token(cls, token: str):
        try:
            user_id = verificar_token_acesso(token)
        except JWTError:
            raise HTTPException(status_code=401, detail="Token inválido ou expirado")

        return user_id
