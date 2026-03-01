from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.security import get_current_active_user

router = APIRouter(prefix="/items", tags=["Items"])

# Simulamos una "base de datos" en memoria para este ejemplo
_items_db: dict = {}
_counter = 0


class ItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    price: float


class ItemResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    price: float
    owner_id: int
    created_at: datetime


@router.get("/", response_model=List[ItemResponse])
async def list_items(current_user=Depends(get_current_active_user)):
    """Listar items del usuario autenticado."""
    return [item for item in _items_db.values() if item["owner_id"] == current_user.id]


@router.post("/", response_model=ItemResponse, status_code=201)
async def create_item(data: ItemCreate, current_user=Depends(get_current_active_user)):
    """Crear un nuevo item."""
    global _counter
    _counter += 1
    item = {
        "id": _counter,
        "title": data.title,
        "description": data.description,
        "price": data.price,
        "owner_id": current_user.id,
        "created_at": datetime.utcnow(),
    }
    _items_db[_counter] = item
    return item


@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, current_user=Depends(get_current_active_user)):
    item = _items_db.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    if item["owner_id"] != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No tienes acceso a este item")
    return item


@router.delete("/{item_id}", status_code=204)
async def delete_item(item_id: int, current_user=Depends(get_current_active_user)):
    item = _items_db.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    if item["owner_id"] != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No puedes eliminar este item")
    del _items_db[item_id]
