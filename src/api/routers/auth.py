from fastapi import APIRouter, HTTPException, status, Request
from src.api import depends
from src.api.schema import UserResponse
from src.api.security.auth import ApiAuthService


router = APIRouter(tags=['Auth'])


@router.post(
    "/login/", 
    summary="Login do usuário",
    description="Autentica um usuário com base nas "
    "credenciais fornecidas e retorna um token de acesso JWT."
)
async def login(
    form_data = depends.form_data,
    user_service = depends.user_service,
):
    auth_service = ApiAuthService()

    user = await user_service.repo.find_by_email(form_data.username)
    if not user or not auth_service.autenticar_usuario(user, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais incorretas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth_service.criar_token_acesso(user.get_id())
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get(
    "/users/me/",
    response_model=UserResponse,
    summary="Obter dados do usuário logado",
    description="Retorna os dados do usuário autenticado "
    "com base no token JWT fornecido."
)
async def ler_meus_dados(user = depends.current_user):
    return user.to_pydantic()
