from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_current_active_user
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserResponse
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Registrar un nuevo usuario."""
    if await user_service.get_user_by_email(user_data.email, db):
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    from app.services.user_service import get_user_by_username
    existing = await get_user_by_username(user_data.username)
    if existing:
        raise HTTPException(status_code=400, detail="El username ya está en uso")

    user = await user_service.create_user(user_data, db)
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Login con username y password. Retorna JWT."""
    from app.services.user_service import get_user_by_username
    user = await get_user_by_username(form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")

    token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user=Depends(get_current_active_user)):
    """Obtener datos del usuario autenticado."""
    return current_user
