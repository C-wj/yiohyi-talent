from fastapi import APIRouter, Depends, HTTPException, Query, Body, Path, status
from typing import List, Optional
from datetime import datetime

from app.models.shopping_list import (
    ShoppingListCreate, 
    ShoppingListUpdate, 
    ShoppingListResponse, 
    ShoppingListItemCreate,
    ShoppingListItemUpdate,
    ShoppingListStatus
)
from app.dependencies.auth import get_current_user
from app.dependencies.database import get_db
from app.services.shopping_list_service import ShoppingListService
from app.models.user import UserResponse

router = APIRouter(
    prefix="/shopping-lists",
    tags=["shopping-lists"],
)


@router.post("", response_model=ShoppingListResponse, status_code=status.HTTP_201_CREATED)
async def create_shopping_list(
    shopping_list: ShoppingListCreate,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Create a new shopping list.
    """
    shopping_list_service = ShoppingListService(db)
    return await shopping_list_service.create_shopping_list(shopping_list, current_user.id)


@router.get("", response_model=List[ShoppingListResponse])
async def get_shopping_lists(
    status: Optional[ShoppingListStatus] = None,
    family_id: Optional[str] = None,
    plan_id: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get all shopping lists with optional filters.
    """
    shopping_list_service = ShoppingListService(db)
    return await shopping_list_service.get_shopping_lists(
        user_id=current_user.id,
        status=status,
        family_id=family_id,
        plan_id=plan_id,
        date_from=date_from,
        date_to=date_to
    )


@router.get("/{shopping_list_id}", response_model=ShoppingListResponse)
async def get_shopping_list(
    shopping_list_id: str = Path(..., title="The ID of the shopping list to get"),
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get a specific shopping list by ID.
    """
    shopping_list_service = ShoppingListService(db)
    shopping_list = await shopping_list_service.get_shopping_list_by_id(shopping_list_id, current_user.id)
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found"
        )
    return shopping_list


@router.put("/{shopping_list_id}", response_model=ShoppingListResponse)
async def update_shopping_list(
    shopping_list_id: str = Path(..., title="The ID of the shopping list to update"),
    shopping_list_update: ShoppingListUpdate = Body(...),
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Update a shopping list.
    """
    shopping_list_service = ShoppingListService(db)
    shopping_list = await shopping_list_service.update_shopping_list(
        shopping_list_id, shopping_list_update, current_user.id
    )
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found"
        )
    return shopping_list


@router.delete("/{shopping_list_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shopping_list(
    shopping_list_id: str = Path(..., title="The ID of the shopping list to delete"),
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Delete a shopping list.
    """
    shopping_list_service = ShoppingListService(db)
    result = await shopping_list_service.delete_shopping_list(shopping_list_id, current_user.id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found"
        )
    return None


@router.post("/{shopping_list_id}/items", response_model=ShoppingListResponse)
async def add_item_to_shopping_list(
    shopping_list_id: str = Path(..., title="The ID of the shopping list"),
    item: ShoppingListItemCreate = Body(...),
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Add an item to a shopping list.
    """
    shopping_list_service = ShoppingListService(db)
    shopping_list = await shopping_list_service.add_item_to_shopping_list(
        shopping_list_id, item, current_user.id
    )
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found"
        )
    return shopping_list


@router.put("/{shopping_list_id}/items/{item_id}", response_model=ShoppingListResponse)
async def update_shopping_list_item(
    shopping_list_id: str = Path(..., title="The ID of the shopping list"),
    item_id: str = Path(..., title="The ID of the item to update"),
    item_update: ShoppingListItemUpdate = Body(...),
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Update an item in a shopping list.
    """
    shopping_list_service = ShoppingListService(db)
    shopping_list = await shopping_list_service.update_shopping_list_item(
        shopping_list_id, item_id, item_update, current_user.id
    )
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list or item not found"
        )
    return shopping_list


@router.delete("/{shopping_list_id}/items/{item_id}", response_model=ShoppingListResponse)
async def remove_item_from_shopping_list(
    shopping_list_id: str = Path(..., title="The ID of the shopping list"),
    item_id: str = Path(..., title="The ID of the item to remove"),
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Remove an item from a shopping list.
    """
    shopping_list_service = ShoppingListService(db)
    shopping_list = await shopping_list_service.remove_item_from_shopping_list(
        shopping_list_id, item_id, current_user.id
    )
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list or item not found"
        )
    return shopping_list


@router.put("/{shopping_list_id}/complete", response_model=ShoppingListResponse)
async def complete_shopping_list(
    shopping_list_id: str = Path(..., title="The ID of the shopping list to complete"),
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Mark a shopping list as completed.
    """
    shopping_list_service = ShoppingListService(db)
    shopping_list = await shopping_list_service.complete_shopping_list(shopping_list_id, current_user.id)
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found"
        )
    return shopping_list


@router.post("/{shopping_list_id}/share", response_model=ShoppingListResponse)
async def share_shopping_list(
    shopping_list_id: str = Path(..., title="The ID of the shopping list to share"),
    user_ids: List[str] = Body(..., embed=True),
    current_user: UserResponse = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Share a shopping list with other users.
    """
    shopping_list_service = ShoppingListService(db)
    shopping_list = await shopping_list_service.share_shopping_list(
        shopping_list_id, user_ids, current_user.id
    )
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found"
        )
    return shopping_list 