from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserAdminUpdate
from app.core.security import hash_password
from app.core.database import AsyncSessionLocal


async def get_user_by_username(username: str) -> Optional[User]:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()


async def get_user_by_email(email: str, db: AsyncSession) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(user_id: int, db: AsyncSession) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 20) -> List[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return result.scalars().all()


async def create_user(user_data: UserCreate, db: AsyncSession) -> User:
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def update_user(user: User, data: UserUpdate, db: AsyncSession) -> User:
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    await db.flush()
    await db.refresh(user)
    return user


async def admin_update_user(user: User, data: UserAdminUpdate, db: AsyncSession) -> User:
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    await db.flush()
    await db.refresh(user)
    return user


async def delete_user(user: User, db: AsyncSession) -> None:
    await db.delete(user)
    await db.flush()


async def create_initial_admin(db: AsyncSession) -> None:
    existing = await db.execute(select(User).where(User.username == "admin"))
    if existing.scalar_one_or_none():
        return
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=hash_password("admin1234"),
        full_name="Administrador",
        role="admin",
    )
    db.add(admin)
    await db.flush()
