from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.core.security import get_current_active_user, get_admin_user
from app.schemas.user import UserResponse, UserUpdate, UserAdminUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_admin_user),  # Solo admins
):
    """Listar todos los usuarios (solo admin)."""
    return await user_service.get_all_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Obtener usuario por ID. Un user solo puede ver su perfil; admin puede ver cualquiera."""
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso")
    
    user = await user_service.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    """Actualizar datos propios."""
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Solo puedes editar tu propio perfil")
    
    user = await user_service.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return await user_service.update_user(user, data, db)


@router.patch("/{user_id}/admin", response_model=UserResponse)
async def admin_update_user(
    user_id: int,
    data: UserAdminUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_admin_user),
):
    """Admin: cambiar rol o estado activo de un usuario."""
    user = await user_service.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return await user_service.admin_update_user(user, data, db)


@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_admin_user),
):
    """Eliminar usuario (solo admin)."""
    user = await user_service.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    await user_service.delete_user(user, db)
