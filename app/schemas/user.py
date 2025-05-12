from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, EmailStr

from app.models.user import Gender, UserRole


class UserProfileBase(BaseModel):
    """用户个人资料基础模型"""
    nickname: str
    avatar: Optional[str] = None
    gender: Gender = Gender.UNKNOWN
    bio: Optional[str] = None
    location: Optional[str] = None
    birthday: Optional[datetime] = None
    website: Optional[str] = None
    profession: Optional[str] = None
    interests: List[str] = Field(default_factory=list)
    background_image: Optional[str] = None


class DietaryPreferenceBase(BaseModel):
    """饮食偏好基础模型"""
    dietary: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    favorite_cuisines: List[str] = Field(default_factory=list)
    disliked_ingredients: List[str] = Field(default_factory=list)
    preferred_meal_time: Optional[str] = None
    preferred_portion_size: Optional[str] = None
    health_goals: List[str] = Field(default_factory=list)
    taste_preferences: Dict[str, int] = Field(default_factory=dict)  # 例如: {"酸": 5, "甜": 3}


class NotificationSettingsBase(BaseModel):
    """通知设置基础模型"""
    email_notifications: bool = True
    push_notifications: bool = True
    sms_notifications: bool = False
    activity_notifications: bool = True
    marketing_notifications: bool = False
    comment_notifications: bool = True
    follower_notifications: bool = True
    like_notifications: bool = True
    message_notifications: bool = True


class UserStatsResponse(BaseModel):
    """用户统计响应模型"""
    recipe_count: int
    favorite_count: int
    order_count: int
    followers_count: int
    following_count: int
    rating_avg: Optional[float] = None
    review_count: int = 0
    contribution_score: int = 0


class UserBase(BaseModel):
    """用户基础模型"""
    profile: UserProfileBase
    preferences: Optional[DietaryPreferenceBase] = None
    notification_settings: Optional[NotificationSettingsBase] = None


class UserCreate(UserBase):
    """用户创建模型"""
    code: str  # 微信临时登录凭证


class UserUpdate(BaseModel):
    """用户更新模型"""
    profile: Optional[UserProfileBase] = None
    preferences: Optional[DietaryPreferenceBase] = None
    notification_settings: Optional[NotificationSettingsBase] = None


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


# 添加密码登录请求模型
class PasswordLoginRequest(BaseModel):
    """账号密码登录请求"""
    account: str
    password: str


# 添加短信验证码请求模型
class SmsRequest(BaseModel):
    """短信验证码发送请求"""
    phoneNumber: str


# 添加短信验证码验证请求模型
class SmsVerifyRequest(BaseModel):
    """短信验证码验证请求"""
    phoneNumber: str
    code: str 