"""
首页内容相关模型
"""
from datetime import datetime
from enum import Enum
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.common import PyObjectId


# 内容类型枚举
class ContentType(str, Enum):
    SWIPER = "swiper"        # 轮播图
    FEATURED = "featured"    # 精选推荐
    POPULAR = "popular"      # 热门菜谱
    CATEGORY = "category"    # 分类推荐
    SEASON = "season"        # 应季推荐
    ARTICLE = "article"      # 文章推荐


# 内容状态枚举
class ContentStatus(str, Enum):
    DRAFT = "draft"          # 草稿
    PUBLISHED = "published"  # 已发布
    ARCHIVED = "archived"    # 已归档


# 标签模型
class Tag(BaseModel):
    text: str                # 标签文本
    theme: str = "primary"   # 标签主题样式


# 首页内容基础模型
class HomeContent(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    type: ContentType        # 内容类型
    title: str               # 标题
    image_url: str           # 图片URL
    target_id: Optional[str] = None  # 关联ID（如菜谱ID）
    target_type: Optional[str] = None  # 关联类型（如recipe）
    target_url: Optional[str] = None  # 目标URL（如外部链接）
    description: Optional[str] = None  # 描述
    tags: List[Tag] = []     # 标签列表
    sort_order: int = 0      # 排序顺序
    status: ContentStatus = ContentStatus.PUBLISHED  # 状态
    start_time: Optional[datetime] = None  # 开始展示时间
    end_time: Optional[datetime] = None    # 结束展示时间
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = None  # 创建者ID
    updated_by: Optional[str] = None  # 更新者ID

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "type": "swiper",
                "title": "春季新菜上市",
                "image_url": "/static/home/swiper1.png",
                "target_id": "507f1f77bcf86cd799439012",
                "target_type": "recipe",
                "description": "春季时令菜品，新鲜上市",
                "tags": [
                    {"text": "春季", "theme": "primary"},
                    {"text": "新品", "theme": "success"}
                ],
                "sort_order": 1,
                "status": "published",
                "created_at": "2023-01-01T12:00:00",
                "updated_at": "2023-05-10T15:30:00",
                "created_by": "507f1f77bcf86cd799439013",
                "updated_by": "507f1f77bcf86cd799439013"
            }
        }


# 轮播图请求模型
class SwiperCreate(BaseModel):
    title: str               # 标题
    image_url: str           # 图片URL
    target_id: Optional[str] = None  # 关联ID
    target_type: Optional[str] = None  # 关联类型
    target_url: Optional[str] = None  # 目标URL
    description: Optional[str] = None  # 描述
    tags: List[Tag] = []     # 标签列表
    sort_order: int = 0      # 排序顺序
    status: ContentStatus = ContentStatus.PUBLISHED  # 状态
    start_time: Optional[datetime] = None  # 开始展示时间
    end_time: Optional[datetime] = None    # 结束展示时间


# 轮播图更新模型
class SwiperUpdate(BaseModel):
    title: Optional[str] = None
    image_url: Optional[str] = None
    target_id: Optional[str] = None
    target_type: Optional[str] = None
    target_url: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[Tag]] = None
    sort_order: Optional[int] = None
    status: Optional[ContentStatus] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


# 内容卡片请求模型
class CardCreate(BaseModel):
    title: str               # 标题
    image_url: str           # 图片URL
    target_id: str           # 关联ID（如菜谱ID）
    target_type: str = "recipe"  # 关联类型（默认为菜谱）
    description: Optional[str] = None  # 描述
    tags: List[Tag] = []     # 标签列表
    sort_order: int = 0      # 排序顺序
    status: ContentStatus = ContentStatus.PUBLISHED  # 状态
    start_time: Optional[datetime] = None  # 开始展示时间
    end_time: Optional[datetime] = None    # 结束展示时间


# 内容卡片更新模型
class CardUpdate(BaseModel):
    title: Optional[str] = None
    image_url: Optional[str] = None
    target_id: Optional[str] = None
    target_type: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[Tag]] = None
    sort_order: Optional[int] = None
    status: Optional[ContentStatus] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


# 查询参数模型
class ContentFilter(BaseModel):
    type: Optional[ContentType] = None
    status: Optional[ContentStatus] = None
    title: Optional[str] = None
    tag: Optional[str] = None


# 首页内容响应模型（简化版，用于前端展示）
class HomeContentResponse(BaseModel):
    id: str
    type: str
    title: str
    image_url: str
    target_id: Optional[str] = None
    target_type: Optional[str] = None
    target_url: Optional[str] = None
    description: Optional[str] = None
    tags: List[Tag] = []
    
    class Config:
        allow_population_by_field_name = True 