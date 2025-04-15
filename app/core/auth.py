from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pymongo.errors import PyMongoError

from app.core.config import settings
from app.db.mongodb import get_collection
from app.models.user import TokenData, UserModel

# JWT配置
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 密码处理工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2认证
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def verify_password(plain_password, hashed_password):
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """生成密码哈希"""
    return pwd_context.hash(password)


async def get_user_by_username(username: str) -> Optional[UserModel]:
    """根据用户名获取用户"""
    users_collection = get_collection("users")
    user_doc = await users_collection.find_one({"username": username})
    if user_doc:
        user_doc["id"] = str(user_doc.pop("_id"))
        return UserModel(**user_doc)
    return None


async def authenticate_user(username: str, password: str) -> Optional[UserModel]:
    """验证用户"""
    user = await get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user.passwordHash):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建JWT访问令牌"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserModel:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码JWT令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
        
    # 获取用户信息
    user = await get_user_by_username(token_data.username)
    if user is None:
        raise credentials_exception
        
    return user


async def get_current_active_user(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    """获取当前活跃用户"""
    if not current_user.isActive:
        raise HTTPException(status_code=400, detail="账号已被禁用")
    return current_user


async def update_last_login(user_id: str) -> bool:
    """更新用户最后登录时间"""
    try:
        users_collection = get_collection("users")
        result = await users_collection.update_one(
            {"_id": user_id},
            {"$set": {"lastLoginAt": datetime.utcnow()}}
        )
        return result.modified_count > 0
    except PyMongoError:
        return False 