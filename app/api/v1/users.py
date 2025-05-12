from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime

from app.api.dependencies import get_current_user
from app.schemas.user import UserResponse, UserProfileBase, DietaryPreferenceBase, NotificationSettingsBase
from app.services.user import update_user

router = APIRouter()

@router.get("/")
async def get_users():
    """
    获取用户列表（示例）
    """
    return {"message": "用户路由创建成功"}


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """
    获取当前用户的个人资料
    
    - 需要授权: Bearer Token
    - 返回用户详细信息
    """
    try:
        return UserResponse(
            id=current_user["_id"],
            openid=current_user["openid"],
            profile=current_user["profile"],
            preferences=current_user.get("preferences"),
            roles=current_user.get("roles", ["user"]),
            stats=current_user["stats"],
            is_verified=current_user.get("is_verified", False),
            created_at=current_user["created_at"],
            updated_at=current_user["updated_at"],
            notification_settings=current_user.get("notification_settings")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户资料失败: {str(e)}"
        )


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    profile: UserProfileBase,
    current_user: dict = Depends(get_current_user)
):
    """
    更新用户个人资料
    
    - 需要授权: Bearer Token
    - 更新用户基本信息
    """
    try:
        user_id = current_user["_id"]
        updated_user = await update_user(user_id, {"profile": profile.dict(), "updated_at": datetime.utcnow()})
        
        return UserResponse(
            id=updated_user["_id"],
            openid=updated_user["openid"],
            profile=updated_user["profile"],
            preferences=updated_user.get("preferences"),
            roles=updated_user.get("roles", ["user"]),
            stats=updated_user["stats"],
            is_verified=updated_user.get("is_verified", False),
            created_at=updated_user["created_at"],
            updated_at=updated_user["updated_at"],
            notification_settings=updated_user.get("notification_settings")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户资料失败: {str(e)}"
        )


@router.put("/preferences", response_model=UserResponse)
async def update_user_preferences(
    preferences: DietaryPreferenceBase,
    current_user: dict = Depends(get_current_user)
):
    """
    更新用户饮食偏好
    
    - 需要授权: Bearer Token
    - 更新用户饮食偏好信息
    """
    try:
        user_id = current_user["_id"]
        updated_user = await update_user(user_id, {"preferences": preferences.dict(), "updated_at": datetime.utcnow()})
        
        return UserResponse(
            id=updated_user["_id"],
            openid=updated_user["openid"],
            profile=updated_user["profile"],
            preferences=updated_user.get("preferences"),
            roles=updated_user.get("roles", ["user"]),
            stats=updated_user["stats"],
            is_verified=updated_user.get("is_verified", False),
            created_at=updated_user["created_at"],
            updated_at=updated_user["updated_at"],
            notification_settings=updated_user.get("notification_settings")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户饮食偏好失败: {str(e)}"
        )


@router.put("/notification-settings", response_model=UserResponse)
async def update_notification_settings(
    settings: NotificationSettingsBase,
    current_user: dict = Depends(get_current_user)
):
    """
    更新用户通知设置
    
    - 需要授权: Bearer Token
    - 更新用户通知设置
    """
    try:
        user_id = current_user["_id"]
        updated_user = await update_user(user_id, {"notification_settings": settings.dict(), "updated_at": datetime.utcnow()})
        
        return UserResponse(
            id=updated_user["_id"],
            openid=updated_user["openid"],
            profile=updated_user["profile"],
            preferences=updated_user.get("preferences"),
            roles=updated_user.get("roles", ["user"]),
            stats=updated_user["stats"],
            is_verified=updated_user.get("is_verified", False),
            created_at=updated_user["created_at"],
            updated_at=updated_user["updated_at"],
            notification_settings=updated_user.get("notification_settings")
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户通知设置失败: {str(e)}"
        )
