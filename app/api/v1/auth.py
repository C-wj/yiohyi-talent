from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.api.dependencies import get_current_user
from app.core.exceptions import AuthenticationError
from app.schemas.user import (
    WechatLoginRequest,
    WechatLoginResponse,
    Token,
    RefreshToken,
    UserResponse,
)
from app.services.auth import wechat_login, refresh_token, logout
from pydantic import BaseModel

router = APIRouter()


@router.post("/wechat-login", response_model=WechatLoginResponse)
async def login_with_wechat(login_request: WechatLoginRequest):
    """
    微信小程序登录
    
    - **code**: 小程序登录时获取的临时登录凭证
    - **user_info**: 可选的用户信息（包含昵称、头像等）
    """
    try:
        user, token, session_key = await wechat_login(login_request.code, login_request.user_info)
        
        # 构建响应
        response = WechatLoginResponse(
            user=UserResponse(**user),
            access_token=token.access_token,
            refresh_token=token.refresh_token,
            token_type=token.token_type,
            session_key=session_key
        )
        
        return response
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.detail),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"微信登录失败: {str(e)}"
        )


@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_data: RefreshToken):
    """
    刷新访问令牌
    
    - **refresh_token**: 刷新令牌
    """
    try:
        new_token = await refresh_token(refresh_data.refresh_token)
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


@router.post("/logout")
async def user_logout(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="token")),
    current_user: dict = Depends(get_current_user)
):
    """
    用户登出
    
    - 需要授权: Bearer Token
    - 将当前令牌加入黑名单
    """
    try:
        result = await logout(token)
        return {"message": "登出成功"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"登出失败: {str(e)}"
        ) 