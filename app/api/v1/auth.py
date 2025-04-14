from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_current_user
from app.core.exceptions import AuthenticationError
from app.schemas.user import (
    WechatLoginRequest,
    WechatLoginResponse,
    Token,
    RefreshToken,
    UserResponse
)
from app.services.auth import wechat_login, refresh_token

router = APIRouter()


@router.post("/login", response_model=WechatLoginResponse)
async def login_with_wechat(login_request: WechatLoginRequest):
    """
    使用微信小程序登录
    
    - **code**: 微信小程序登录时获取的临时登录凭证code
    - **user_info**: 可选的用户信息（包含昵称、头像等）
    """
    try:
        user, token, session_key = await wechat_login(login_request.code, login_request.user_info)
        
        # 转换为响应模型
        user_response = UserResponse(
            id=user["_id"],
            openid=user["openid"],
            profile=user["profile"],
            preferences=user.get("preferences"),
            roles=user.get("roles", ["user"]),
            stats=user["stats"],
            is_verified=user.get("is_verified", False),
            created_at=user["created_at"],
            updated_at=user["updated_at"]
        )
        
        return WechatLoginResponse(
            session_key=session_key,
            user=user_response,
            token=token
        )
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.detail),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登录失败: {str(e)}"
        )


@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_token_req: RefreshToken):
    """
    刷新访问令牌
    
    - **refresh_token**: 刷新令牌
    """
    try:
        new_token = await refresh_token(refresh_token_req.refresh_token)
        return new_token
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.detail),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"刷新令牌失败: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    获取当前用户信息
    
    需要授权: Bearer Token
    """
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