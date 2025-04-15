from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum
import secrets

from pydantic import BaseModel, Field


class FamilyMemberRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class FamilyMemberBase(BaseModel):
    nickname: str
    role: str = "member"  # "creator", "admin", "member"
    permissions: List[str] = ["view", "edit"]


class FamilyMemberAdd(FamilyMemberBase):
    user_id: str


class FamilyMemberUpdate(BaseModel):
    nickname: Optional[str] = None
    role: Optional[str] = None
    permissions: Optional[List[str]] = None


class FamilyMemberResponse(FamilyMemberBase):
    user_id: str
    avatar: Optional[str] = None
    joined_at: datetime


class FamilyInvitationCreate(BaseModel):
    expiry_hours: int = 24
    max_uses: Optional[int] = None


class FamilyInvitationResponse(BaseModel):
    invitation_id: str
    code: str
    created_by: str
    created_at: datetime
    expires_at: datetime
    max_uses: Optional[int] = None
    used_count: int = 0


class FamilyCreate(BaseModel):
    name: str
    avatar: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class FamilyUpdate(BaseModel):
    name: Optional[str] = None
    avatar: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class FamilyResponse(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    avatar: Optional[str] = None
    creator: str
    members: List[FamilyMemberResponse]
    settings: Optional[Dict[str, Any]] = None
    invitations: Optional[List[FamilyInvitationResponse]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class FamilyModel(BaseModel):
    name: str
    avatar: Optional[str] = None
    creator: str  # 创建者用户ID
    members: List[FamilyMember] = Field(default_factory=list)
    settings: FamilySetting = Field(default_factory=FamilySetting)
    invitations: List[FamilyInvitation] = Field(default_factory=list)
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)


class FamilyInvitation(BaseModel):
    code: str = Field(default_factory=lambda: secrets.token_urlsafe(8))
    createdBy: str  # 创建者用户ID
    expiresAt: datetime = Field(default_factory=lambda: datetime.now() + timedelta(days=7))
    isUsed: bool = False
    usedBy: Optional[str] = None  # 使用者用户ID
    usedAt: Optional[datetime] = None


class FamilySetting(BaseModel):
    theme: str = "default"
    mealReminders: bool = True
    shoppingReminders: bool = True
    autoShareRecipes: bool = True
    defaultCuisinePreference: Optional[str] = None


class FamilyMember(BaseModel):
    userId: str
    nickname: str
    avatar: Optional[str] = None
    role: FamilyMemberRole = FamilyMemberRole.MEMBER
    joinedAt: datetime = Field(default_factory=datetime.now)


# API请求响应模型
class FamilyInvitationUse(BaseModel):
    code: str


class FamilyResponse(BaseModel):
    id: str
    name: str
    avatar: Optional[str] = None
    creator: str
    members: List[FamilyMember]
    settings: FamilySetting
    invitations: List[FamilyInvitation] = []
    createdAt: datetime
    updatedAt: datetime 