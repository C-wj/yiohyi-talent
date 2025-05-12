"""
认证依赖注入
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError

from app.core.config import settings
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.core.security import decode_token
from app.db.mongodb import get_collection, USERS_COLLECTION
from app.models.user import UserResponse
from app.services.auth import is_token_blacklisted

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    获取当前已认证用户
    
    依赖项：验证JWT令牌并返回当前用户
    
    若验证失败，抛出认证错误
    """
    try:
        # 检查令牌是否已被列入黑名单
        if await is_token_blacklisted(token):
            raise AuthenticationError(detail="令牌已失效，请重新登录")
            
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError(detail="无效的认证信息")
    except (JWTError, ValidationError) as e:
        raise AuthenticationError(detail=f"无效的认证凭据: {str(e)}")
    
    # 从数据库获取用户
    users_collection = get_collection("users")
    user = await users_collection.find_one({"_id": user_id})
    
    if not user:
        raise AuthenticationError(detail="用户不存在")
    
    if not user.get("is_active", False):
        raise AuthenticationError(detail="用户已被禁用")
    
    return user 