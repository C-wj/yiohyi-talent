from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from bson.objectid import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.db.mongodb import get_collection
from app.models.user import TokenData, UserResponse

# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_PREFIX}/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    生成密码哈希
    """
    return pwd_context.hash(password)


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建刷新令牌
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """解码令牌"""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except (jwt.JWTError, ValidationError):
        raise ValueError("Invalid token")


def get_token_data(token: str) -> Dict[str, Any]:
    """
    获取令牌数据
    """
    payload = decode_token(token)
    return payload


def generate_password_reset_token(email: str) -> str:
    """
    生成密码重置令牌
    """
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode = {"exp": expire, "sub": email, "type": "reset"}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_password_reset_token(token: str) -> str:
    """
    验证密码重置令牌
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        if payload.get("type") != "reset":
            raise AuthenticationError(detail="无效的重置令牌类型")
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        raise AuthenticationError(detail="重置令牌已过期")
    except (jwt.JWTError, ValidationError):
        raise AuthenticationError(detail="无效的重置令牌")


async def get_user(username: str) -> Optional[Dict[str, Any]]:
    """通过用户名获取用户信息"""
    if not username:
        return None
    users_collection = get_collection("users")
    user = await users_collection.find_one({"username": username})
    return user


async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """通过邮箱获取用户信息"""
    if not email:
        return None
    users_collection = get_collection("users")
    user = await users_collection.find_one({"email": email})
    return user


async def authenticate_user(username: str, password: str) -> Union[Dict[str, Any], bool]:
    """验证用户"""
    user = await get_user(username)
    if not user:
        return False
    if not verify_password(password, user["passwordHash"]):
        return False
    return user 