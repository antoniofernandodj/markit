import traceback
from contextlib import suppress
from typing import Optional
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import NoResultFound
from src.api.security.auth import ApiAuthService
from src.database.entities import AsyncSessionFactory
from src.domain import exceptions


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

def register_exceptions(app: FastAPI):

    @app.exception_handler(NoResultFound)
    async def not_result_found_handler(request: Request, exception: Exception):
        detail = str(exception) or 'Item não encontrado!'
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"{exception.__class__.__name__}: {detail}"}
        )

    @app.exception_handler(exceptions.PermissaoNaoConcedidaException)
    async def permissao_nao_concedida_handler(request: Request, exception: Exception):
        detail = str(exception) or 'Permissão não concedida!'
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": f"{exception.__class__.__name__}: {detail}"}
        )

    @app.exception_handler(exceptions.UsuarioNaoEncontradoException)
    async def usuario_nao_encontrado_handler(request: Request, exception: Exception):
        detail = str(exception) or 'Usuario não encontrado!'
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"{exception.__class__.__name__}: {detail}"}
        )

    @app.exception_handler(exceptions.EmailJaCadastradoException)
    async def email_ja_cadastrado_handler(request: Request, exception: Exception):
        detail = str(exception) or 'Usuario já cadastrado!'
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": f"{exception.__class__.__name__}: {detail}"}
        )

    @app.exception_handler(exceptions.CalendarioNaoEncontradoException)
    async def calendario_nao_encontrado_handler(request: Request, exception: Exception):
        detail = str(exception) or 'Calendario não encontrado!'
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"{exception.__class__.__name__}: {detail}"}
        )

    @app.exception_handler(exceptions.EventoNaoEncontradoException)
    async def evento_nao_encontrado_handler(request: Request, exception: Exception):
        detail = str(exception) or "Evento não encontrado"
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"{exception.__class__.__name__}: {detail}"}
        )

    @app.exception_handler(exceptions.CompartilhamentoJaExistenteException)
    async def compartilhamento_ja_existente_handler(request: Request, exception: Exception):
        detail = str(exception) or 'Compartilhamento já cadastrado!'
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": f"{exception.__class__.__name__}: {detail}"}
        )

    @app.exception_handler(exceptions.CompartilhamentoNaoEncontradoException)
    async def compartilhamento_nao_encontrado_handler(request: Request, exception: Exception):
        detail = str(exception) or "Compartilhamento não encontrado"
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": f"{exception.__class__.__name__}: {detail}"}
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exception: Exception):
        detail = str(exception)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": f"Internal Server Error: {detail}",
                "traceback": "... " + traceback.format_exc(limit=2)
            }
        )

async def get_logged_in_id(token: Optional[str]) -> Optional[str]:
    auth_service = ApiAuthService()
    logged_user_id = None
    with suppress(Exception):
        logged_user_id = await auth_service.obter_usuario_pelo_token(token or '')

    return logged_user_id

async def get_session():
    async with AsyncSessionFactory() as session:
        yield session
