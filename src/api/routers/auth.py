from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from src.api import depends
from src.api.schema import LoginResponse, UserResponse
from src.api.security.auth import ApiAuthService
from fastapi_utils.cbv import cbv

from src.domain.models.user import User
from src.domain.services.user_service import UserService


router = APIRouter(tags=['Auth'])


@cbv(router)
class AuthController:

    user_service: UserService = depends.user_service

    @router.post(
        "/login/", 
        response_model=LoginResponse,
        summary="Login do usuário",
        description="Autentica um usuário com base nas "
        "credenciais fornecidas e retorna um token de acesso JWT."
    )
    async def login(
        self,
        form_data: OAuth2PasswordRequestForm = depends.form_data
    ):
        auth_service = ApiAuthService()

        user = await self.user_service.repo.find_by_email(form_data.username)
        if not user or not auth_service.autenticar_usuario(user, form_data.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais incorretas",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = auth_service.criar_token_acesso(user.get_id())
        return LoginResponse(access_token=access_token, token_type='bearer')

    @router.get(
        "/users/me/",
        response_model=UserResponse,
        summary="Obter dados do usuário logado",
        description="Retorna os dados do usuário autenticado "
        "com base no token JWT fornecido."
    )
    async def ler_meus_dados(
        self,
        current_user: User = depends.current_user
    ):
        return current_user.to_pydantic()
