from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime

from app.api.dependencies import get_current_user
from app.models.user import UserResponse, UserProfileBase, DietaryPreferenceBase, NotificationSettingsBase, BaseResponse
from app.services.user import update_user, get_user_by_id
from app.core.decorators import api_response
from app.core.response import not_found_response

router = APIRouter()

@router.get("/")
@api_response
async def get_users():
    """
    获取用户列表（示例）
    """
    # 示例用户数据
    users = [
        {"id": "1", "username": "test1", "email": "test1@example.com"},
        {"id": "2", "username": "test2", "email": "test2@example.com"}
    ]
    return users


@router.get("/profile")
@api_response
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """
    获取当前用户信息
    
    - 需要授权: Bearer Token
    - 返回用户详细信息
    """
    # 通过ID获取完整的用户信息
    user_id = current_user.get("_id")
    user = await get_user_by_id(user_id)
    
    if not user:
        return not_found_response(msg="用户不存在")
    
    # 直接返回用户对象，它会被正确序列化
    return user


@router.put("/profile")
@api_response
async def update_user_profile(
    profile: UserProfileBase,
    current_user: dict = Depends(get_current_user)
):
    """
    更新用户基础信息
    
    - 需要授权: Bearer Token
    - 返回更新后的用户信息
    """
    updated_user = await update_user(current_user["_id"], {"profile": profile.dict()})
    if not updated_user:
        return not_found_response(msg="用户不存在")
    
    return updated_user


@router.put("/preferences")
@api_response
async def update_user_preferences(
    preferences: DietaryPreferenceBase,
    current_user: dict = Depends(get_current_user)
):
    """
    更新用户饮食偏好
    
    - 需要授权: Bearer Token
    - 返回更新后的偏好信息
    """
    # 更新用户饮食偏好
    updated_user = await update_user(current_user["_id"], {"preferences": preferences.dict()})
    if not updated_user:
        return not_found_response(msg="用户不存在")
    
    # 返回完整的用户对象
    return updated_user


@router.put("/notifications")
@api_response
async def update_notification_settings(
    settings: NotificationSettingsBase,
    current_user: dict = Depends(get_current_user)
):
    """
    更新通知设置
    
    - 需要授权: Bearer Token
    - 返回更新后的通知设置
    """
    # 更新用户通知设置
    updated_user = await update_user(current_user["_id"], {"notification_settings": settings.dict()})
    if not updated_user:
        return not_found_response(msg="用户不存在")
    
    # 返回完整的用户对象
    return updated_user
