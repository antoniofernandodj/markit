from datetime import datetime, timedelta, UTC
from typing import Optional
from jose import JWTError, jwt


SECRET_KEY = "minha_chave_secreta_super_segura"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def criar_token_acesso(dados: dict, expires_delta: Optional[timedelta] = None):
    to_encode = dados.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verificar_token_acesso(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise JWTError()
        return user_id
    except JWTError:
        raise JWTError("Token inválido ou expirado")
