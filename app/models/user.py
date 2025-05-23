from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Generic, TypeVar

from bson import ObjectId
from pydantic import BaseModel, EmailStr, Field, validator

from app.db.mongodb import USERS_COLLECTION
from app.models.common import PyObjectId

T = TypeVar('T')

# 基础响应模型
class BaseResponse(BaseModel, Generic[T]):
    """基础响应模型"""
    status: str
    message: str
    data: Optional[T] = None


class Gender(str, Enum):
    """性别枚举"""
    UNKNOWN = "unknown"
    MALE = "male"
    FEMALE = "female"


class UserRole(str, Enum):
    """用户角色枚举"""
    USER = "user"           # 普通用户
    ADMIN = "admin"         # 管理员
    SUPER_ADMIN = "super_admin"  # 超级管理员


class UserPreferences(BaseModel):
    dietary: List[str] = Field(default_factory=list)  # 饮食偏好
    allergies: List[str] = Field(default_factory=list)  # 过敏原
    favoriteCuisines: List[str] = Field(default_factory=list)  # 喜好菜系
    dislikedIngredients: List[str] = Field(default_factory=list)  # 不喜欢的食材


class UserProfile(BaseModel):
    nickname: str
    avatar: Optional[str] = None
    bio: Optional[str] = None
    gender: Optional[str] = None
    location: Optional[str] = None


class UserStats(BaseModel):
    recipeCount: int = 0  # 创建的菜谱数
    favoriteCount: int = 0  # 收藏的菜谱数
    orderCount: int = 0  # 创建的点菜订单数
    followersCount: int = 0  # 粉丝数
    followingCount: int = 0  # 关注数


class UserSettings(BaseModel):
    notification: bool = True  # 通知设置
    privacy: str = "public"  # 隐私设置:'public','friends','private'
    theme: str = "light"  # 主题设置:'light','dark'


class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    email: Optional[EmailStr] = None
    avatarUrl: Optional[str] = None
    nickname: Optional[str] = None
    bio: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[datetime] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    isActive: bool = True
    isVerified: bool = False


class UserCreate(UserBase):
    """用户创建模型"""
    password: str
    email: Optional[EmailStr] = None
    username: str
    nickname: Optional[str] = None
    phone: Optional[str] = None

    @validator('password')
    def password_validation(cls, v):
        if len(v) < 8:
            raise ValueError('密码长度至少为8位')
        if not any(char.isdigit() for char in v):
            raise ValueError('密码必须包含至少一个数字')
        if not any(char.isupper() for char in v):
            raise ValueError('密码必须包含至少一个大写字母')
        return v
        
    @validator('username')
    def username_validation(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('用户名长度至少为3位')
        return v


class UserUpdate(BaseModel):
    """用户更新模型"""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    avatarUrl: Optional[str] = None
    nickname: Optional[str] = None
    bio: Optional[str] = None
    gender: Optional[str] = None
    birthday: Optional[datetime] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    isActive: Optional[bool] = None
    isVerified: Optional[bool] = None


class UserInDB(UserBase):
    """数据库中的用户模型"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    passwordHash: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: Optional[datetime] = None
    lastLoginAt: Optional[datetime] = None
    favorites: List[str] = []
    following: List[str] = []
    followers: List[str] = []

    class Config:
        schema_extra = {
            "example": {
                "_id": "60d21b4967d0d8992e610c85",
                "username": "user123",
                "email": "user@example.com",
                "avatarUrl": "https://example.com/avatar.jpg",
                "nickname": "User Nick",
                "bio": "About me",
                "gender": "male",
                "birthday": "1990-01-01T00:00:00",
                "location": "New York",
                "phone": "1234567890",
                "passwordHash": "hashed_password",
                "isActive": True,
                "isVerified": False,
                "createdAt": "2023-01-01T00:00:00",
                "updatedAt": "2023-01-02T00:00:00",
                "lastLoginAt": "2023-01-03T00:00:00",
                "favorites": ["60d21b4967d0d8992e610c86"],
                "following": ["60d21b4967d0d8992e610c87"],
                "followers": ["60d21b4967d0d8992e610c88"]
            }
        }


class UserResponse(UserBase):
    """用户响应模型"""
    id: str = Field(..., alias="_id")
    createdAt: datetime
    updatedAt: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True


class Token(BaseModel):
    """访问令牌模型"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class TokenData(BaseModel):
    """令牌数据模型"""
    sub: str
    exp: Optional[int] = None


class User(BaseModel):
    """用户模型"""
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    openid: str                       # 微信openid
    unionid: Optional[str] = None     # 微信unionid(如适用)
    
    profile: UserProfile              # 个人资料
    preferences: UserPreferences = Field(default_factory=UserPreferences)  # 饮食偏好
    stats: UserStats = UserStats()    # 统计数据
    settings: UserSettings = UserSettings()  # 设置
    
    roles: List[UserRole] = [UserRole.USER]  # 用户角色
    is_active: bool = True            # 是否激活
    is_verified: bool = False         # 是否已验证
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    class Config:
        collection = USERS_COLLECTION
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "openid": "oLKQZ5R-VWyZM0VowVZsdQZfS_UM",
                "unionid": "oQ_1w5iGjsyhC-yTvQbvN6-KdQyg",
                "profile": {
                    "nickname": "张三",
                    "avatar": "https://example.com/avatar.jpg",
                    "gender": "male",
                    "bio": "美食爱好者，热爱烹饪家常菜"
                },
                "preferences": {
                    "dietary": ["低脂", "少盐"],
                    "allergies": ["海鲜"],
                    "favoriteCuisines": ["川菜", "粤菜"],
                    "dislikedIngredients": ["香菜"]
                },
                "stats": {
                    "recipeCount": 12,
                    "favoriteCount": 45,
                    "orderCount": 8,
                    "followersCount": 20,
                    "followingCount": 15
                },
                "settings": {
                    "notification": True,
                    "privacy": "public",
                    "theme": "light"
                },
                "roles": ["user"],
                "is_active": True,
                "is_verified": True,
                "createdAt": "2023-01-01T12:00:00",
                "updatedAt": "2023-05-10T15:30:00",
                "lastLoginAt": "2023-05-15T09:20:00"
            }
        }


# 添加用户注册请求模型
class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    username: str  # 必填
    password: str  # 必填
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    
    @validator('username')
    def username_not_empty(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('用户名长度至少为3位')
        if not v.isalnum():
            raise ValueError('用户名只能包含字母和数字')
        return v
        
    @validator('password')
    def password_validation(cls, v):
        if len(v) < 8:
            raise ValueError('密码长度至少为8位')
        if not any(char.isdigit() for char in v):
            raise ValueError('密码必须包含至少一个数字')
        if not any(char.isupper() for char in v):
            raise ValueError('密码必须包含至少一个大写字母')
        return v
    
    @validator('phone')
    def phone_validation(cls, v):
        if v is None or v == "":
            return None
        # 中国手机号验证
        import re
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('无效的手机号码格式')
        return v
    
    @validator('email')
    def email_validation(cls, v):
        if v is None or v == "":
            return None
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "username": "user123",
                "password": "Password123",
                "nickname": "张三",
                "email": "user@example.com",
                "phone": "13800138000"
            }
        }


# 微信登录相关模型
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


# 密码登录请求模型
class PasswordLoginRequest(BaseModel):
    """账号密码登录请求"""
    account: str
    password: str


# 刷新令牌模型
class RefreshToken(BaseModel):
    """刷新令牌模型"""
    refresh_token: str


# 短信验证码相关模型
class PhoneNumberRequest(BaseModel):
    """手机号请求"""
    phone_number: str


class VerifySMSRequest(BaseModel):
    """短信验证码验证请求"""
    phone_number: str
    code: str


# 用户资料相关模型
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