from typing import Optional

from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer

from app.core.exceptions import AuthenticationError
from app.core.security import decode_token
from app.services.user import get_user_by_id

# OAuth2密码流认证
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/api/v1/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    获取当前用户
    """
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise AuthenticationError(detail="无效的令牌")
    except Exception:
        raise AuthenticationError(detail="无效的令牌")
    
    user = await get_user_by_id(user_id)
    if user is None:
        raise AuthenticationError(detail="用户不存在")
    
    return user


async def get_optional_user(token: Optional[str] = Header(None, alias="Authorization")):
    """
    获取可选用户（如果有Token则验证，没有则返回None）
    """
    if not token:
        return None
    
    if token.startswith("Bearer "):
        token = token.replace("Bearer ", "")
    
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            return None
        
        user = await get_user_by_id(user_id)
        return user
    except Exception:
        return None 