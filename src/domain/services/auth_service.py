from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from src.domain.models import User
from src.config import settings

import jwt




class AuthService:

    @classmethod
    def autenticar_usuario(cls, user: User, senha: str) -> bool:
        return bcrypt.checkpw(
            senha.encode('utf-8'),
            user.password_hash.encode('utf-8')
        )

    @classmethod
    def generate_hash(cls, string) -> str:
        return (
            bcrypt
            .hashpw(string.encode('utf-8'), bcrypt.gensalt())
            .decode('utf-8')
        )

    @classmethod
    def generate_token(cls, user: User) -> str:

        return (
            jwt
            .encode(
                {
                    'id': user.get_id(),
                    'email': user.email,
                    'exp': (datetime.utcnow() + timedelta(hours=1)).timestamp()
                },
                str(settings.SECRET_KEY),
                algorithm='HS256'
            )
        )

    @classmethod
    def decode_token(cls, token: str) -> Optional[dict]:
        return jwt.decode(token, str(settings.SECRET_KEY), algorithms=['HS256'])

    @classmethod
    def verify_token(cls, token: str) -> Optional[User]:
        payload = cls.decode_token(token)
        if payload is None:
            return None

        user_id = payload.get('id')
        if user_id is None:
            return None

        # return User.get_by_id(user_id)
