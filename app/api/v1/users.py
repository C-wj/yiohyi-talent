from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime

from app.api.dependencies import get_current_user
from app.schemas.user import UserResponse, UserProfileBase, DietaryPreferenceBase, NotificationSettingsBase, BaseResponse
from app.services.user import update_user
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
    # 用户信息可能在current_user中，或需要从数据库查询更多信息
    user_data = {
        "id": current_user.get("user_id"),
        "username": current_user.get("username"),
        "nickname": current_user.get("nickname", "用户" + current_user.get("user_id", "")[-4:]),
        "avatar": current_user.get("avatar", ""),
        "email": current_user.get("email", ""),
        "phone": current_user.get("phone", ""),
        "created_at": current_user.get("created_at", datetime.now().isoformat()),
        "last_login": current_user.get("last_login", datetime.now().isoformat())
    }
    
    return user_data


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
    updated_user = await update_user(current_user["user_id"], profile.dict())
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
    # 假设有一个服务函数来更新用户偏好
    updated_prefs = await update_user(current_user["user_id"], {"preferences": preferences.dict()})
    if not updated_prefs:
        return not_found_response(msg="用户不存在")
    
    return preferences.dict()


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
    # 假设有一个服务函数来更新通知设置
    updated_settings = await update_user(current_user["user_id"], {"notification_settings": settings.dict()})
    if not updated_settings:
        return not_found_response(msg="用户不存在")
    
    return settings.dict()
