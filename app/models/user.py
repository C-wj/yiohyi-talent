from datetime import datetime
from enum import Enum
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from app.db.mongodb import USERS_COLLECTION


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


class UserProfile(BaseModel):
    """用户个人资料"""
    nickname: str
    avatar: Optional[str] = None
    gender: Gender = Gender.UNKNOWN
    bio: Optional[str] = None


class DietaryPreference(BaseModel):
    """饮食偏好"""
    dietary: List[str] = []           # 饮食习惯，如"素食"、"低脂"
    allergies: List[str] = []          # 过敏原，如"花生"、"海鲜"
    favorite_cuisines: List[str] = []  # 喜好的菜系
    disliked_ingredients: List[str] = [] # 不喜欢的食材


class UserStats(BaseModel):
    """用户统计数据"""
    recipe_count: int = 0
    favorite_count: int = 0
    order_count: int = 0
    followers_count: int = 0
    following_count: int = 0


class User(BaseModel):
    """用户模型"""
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    openid: str                       # 微信openid
    unionid: Optional[str] = None     # 微信unionid(如适用)
    
    profile: UserProfile              # 个人资料
    preferences: Optional[DietaryPreference] = None  # 饮食偏好
    stats: UserStats = UserStats()    # 统计数据
    
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
                    "favorite_cuisines": ["川菜", "粤菜"],
                    "disliked_ingredients": ["香菜"]
                },
                "stats": {
                    "recipe_count": 12,
                    "favorite_count": 45,
                    "order_count": 8,
                    "followers_count": 20,
                    "following_count": 15
                },
                "roles": ["user"],
                "is_active": True,
                "is_verified": True,
                "created_at": "2023-01-01T12:00:00",
                "updated_at": "2023-05-10T15:30:00",
                "last_login": "2023-05-15T09:20:00"
            }
        } 