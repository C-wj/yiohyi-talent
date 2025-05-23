"""
认证依赖注入
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.db.mongodb import get_collection, USERS_COLLECTION
from app.models.user import UserResponse
from app.utils.mongodb_utils import MongoDBUtils

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    获取当前已认证用户
    
    - 依赖于OAuth2PasswordBearer
    - 解析JWT令牌获取用户ID
    - 从数据库查询用户完整信息
    
    为简化项目初期开发，在数据库连接失败时提供模拟用户
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码JWT令牌
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # 从数据库获取用户信息
    users_collection = get_collection(USERS_COLLECTION)
    user = await MongoDBUtils.get_document_by_id(users_collection, user_id)
    
    # 如果用户不存在且为开发环境，提供模拟用户
    if user is None and settings.APP_ENV == "development":
        # 开发环境下，如果用户不存在，返回测试用户
        return {
            "id": "test_user_id",
            "username": "test_user",
            "email": "test@example.com",
            "is_active": True
        }
    
    if user is None:
        raise credentials_exception
        
    # 返回序列化后的用户字典
    return user 