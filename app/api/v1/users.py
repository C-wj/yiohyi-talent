from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.schemas.user import UserResponse

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
            updated_at=current_user["updated_at"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户资料失败: {str(e)}"
        )
