from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, EmailStr

from app.models.user import Gender, UserRole


class UserProfileBase(BaseModel):
    """用户个人资料基础模型"""
    nickname: str
    avatar: Optional[str] = None
    gender: Gender = Gender.UNKNOWN
    bio: Optional[str] = None


class DietaryPreferenceBase(BaseModel):
    """饮食偏好基础模型"""
    dietary: List[str] = []
    allergies: List[str] = []
    favorite_cuisines: List[str] = []
    disliked_ingredients: List[str] = []


class UserStatsResponse(BaseModel):
    """用户统计响应模型"""
    recipe_count: int
    favorite_count: int
    order_count: int
    followers_count: int
    following_count: int


class UserBase(BaseModel):
    """用户基础模型"""
    profile: UserProfileBase
    preferences: Optional[DietaryPreferenceBase] = None


class UserCreate(UserBase):
    """用户创建模型"""
    code: str  # 微信临时登录凭证


class UserUpdate(BaseModel):
    """用户更新模型"""
    profile: Optional[UserProfileBase] = None
    preferences: Optional[DietaryPreferenceBase] = None


class UserResponse(UserBase):
    """用户响应模型"""
    id: str
    openid: str
    roles: List[UserRole]
    stats: UserStatsResponse
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class UserInDB(UserResponse):
    """数据库中的用户模型(管理员视图)"""
    unionid: Optional[str] = None
    is_active: bool
    last_login: Optional[datetime] = None


class Token(BaseModel):
    """令牌模型"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """令牌负载模型"""
    sub: Optional[str] = None
    exp: Optional[int] = None


class RefreshToken(BaseModel):
    """刷新令牌模型"""
    refresh_token: str


class WechatLoginRequest(BaseModel):
    """微信登录请求"""
    code: str
    user_info: Optional[dict] = None


class WechatLoginResponse(BaseModel):
    """微信登录响应"""
    session_key: str
    user: UserResponse
    token: Token


class WechatBindRequest(BaseModel):
    """微信绑定请求"""
    code: str
    open_id: str 