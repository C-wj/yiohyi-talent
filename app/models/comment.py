from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, conint


class CommentBase(BaseModel):
    """评论基础模型"""
    content: str = Field(..., min_length=1, max_length=500)
    rating: conint(ge=1, le=5)  # 1-5星评分
    images: Optional[List[str]] = None  # 评论图片URL列表


class CommentCreate(CommentBase):
    """评论创建模型"""
    pass


class CommentUpdate(BaseModel):
    """评论更新模型"""
    content: Optional[str] = Field(None, min_length=1, max_length=500)
    rating: Optional[conint(ge=1, le=5)] = None
    images: Optional[List[str]] = None


class UserBrief(BaseModel):
    """用户简要信息"""
    id: str
    name: str
    avatar: Optional[str] = None


class CommentResponse(CommentBase):
    """评论响应模型"""
    id: str
    user: UserBrief
    recipe_id: str
    likes: int = 0
    created_at: datetime
    updated_at: datetime


class CommentListResponse(BaseModel):
    """评论列表响应模型"""
    comments: List[CommentResponse]
    total: int
    page: int
    limit: int
    pages: int 