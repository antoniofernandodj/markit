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
    def __init__(self):
        self.auth_service = AuthService()

    def autenticar_usuario(self, usuario: User, senha: str) -> bool:
        return self.auth_service.autenticar_usuario(usuario, senha)

    def criar_token_acesso(self, user_id: str):
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        return criar_token_acesso({"sub": user_id}, expires_delta=access_token_expires)

    async def obter_usuario_pelo_token(self, token: str):
        try:
            user_id = verificar_token_acesso(token)
        except JWTError:
            raise HTTPException(status_code=401, detail="Token inválido ou expirado")

        return user_id
