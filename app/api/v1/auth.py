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
    PasswordLoginRequest,
    UserRegisterRequest,
)
from app.services.auth import wechat_login, refresh_token, logout, password_login, register_user
from app.core.decorators import api_response
import logging

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/wechat-login")
@api_response
async def login_with_wechat(login_request: WechatLoginRequest):
    """
    微信小程序登录
    
    - **code**: 小程序登录时获取的临时登录凭证
    - **user_info**: 可选的用户信息（包含昵称、头像等）
    """
    user, token, session_key = await wechat_login(login_request.code, login_request.user_info)
    
    # 构建响应
    response = {
        "user": user,
        "access_token": token.access_token,
        "refresh_token": token.refresh_token,
        "token_type": token.token_type,
        "session_key": session_key
    }
    
    return response


@router.post("/register")
@api_response
async def register(register_data: UserRegisterRequest):
    """
    用户注册
    
    - **username**: 用户名
    - **password**: 密码
    - **email**: 邮箱（可选）
    - **phone**: 手机号（可选）
    - **nickname**: 昵称
    """
    token = await register_user(register_data)
    return token


@router.post("/login")
@api_response
async def login(login_data: PasswordLoginRequest):
    """
    账号密码登录
    
    - **account**: 账号（用户名/手机号/邮箱）
    - **password**: 密码
    """
    token = await password_login(login_data.account, login_data.password)
    return token


@router.post("/refresh")
@api_response
async def refresh_access_token(refresh_data: RefreshToken):
    """
    刷新访问令牌
    
    - **refresh_token**: 刷新令牌
    """
    new_token = await refresh_token(refresh_data.refresh_token)
    return new_token


@router.post("/logout")
@api_response
async def user_logout(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="token")),
    current_user: dict = Depends(get_current_user)
):
    """
    用户登出
    
    - 需要授权: Bearer Token
    - 将当前令牌加入黑名单
    """
    await logout(token)
    return {"message": "登出成功"} 