from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field, validator


class ShoppingListStatus(str, Enum):
    """购物清单状态枚举"""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"


class ShoppingItemCategory(str, Enum):
    VEGETABLES = "vegetables"
    FRUITS = "fruits"
    MEAT = "meat"
    SEAFOOD = "seafood"
    DAIRY = "dairy"
    BAKERY = "bakery"
    PANTRY = "pantry"
    FROZEN = "frozen"
    BEVERAGES = "beverages"
    SNACKS = "snacks"
    HOUSEHOLD = "household"
    OTHER = "other"


class ShoppingListItemBase(BaseModel):
    """购物清单条目基本模型"""
    name: str
    quantity: float
    unit: str
    category: ShoppingItemCategory = ShoppingItemCategory.OTHER
    estimated_price: Optional[float] = None
    note: Optional[str] = None
    is_purchased: bool = False
    priority: Optional[str] = None


class ShoppingListItemCreate(ShoppingListItemBase):
    """创建购物清单条目的请求模型"""
    pass


class ShoppingListItemUpdate(BaseModel):
    """更新购物清单条目的请求模型"""
    name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    category: Optional[ShoppingItemCategory] = None
    estimated_price: Optional[float] = None
    is_purchased: Optional[bool] = None
    note: Optional[str] = None
    priority: Optional[str] = None
    purchased_by: Optional[str] = None
    purchased_at: Optional[datetime] = None


class ShoppingListItemResponse(ShoppingListItemBase):
    """购物清单条目的响应模型"""
    id: str
    purchased_by: Optional[str] = None
    purchased_at: Optional[datetime] = None
    

class ShoppingListBase(BaseModel):
    """购物清单基本模型"""
    name: str
    family_id: Optional[str] = None
    plan_id: Optional[str] = None
    date: datetime = Field(default_factory=datetime.now)
    status: ShoppingListStatus = ShoppingListStatus.DRAFT
    total_cost: Optional[float] = None
    shared_with: Optional[List[str]] = None


class ShoppingListCreate(ShoppingListBase):
    """创建购物清单的请求模型"""
    items: List[ShoppingListItemCreate] = []


class ShoppingListUpdate(BaseModel):
    """更新购物清单的请求模型"""
    name: Optional[str] = None
    date: Optional[datetime] = None
    total_cost: Optional[float] = None
    status: Optional[ShoppingListStatus] = None


class ShoppingListResponse(ShoppingListBase):
    """购物清单的响应模型"""
    id: str
    items: List[ShoppingListItemResponse] = []
    creator_id: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    @validator('completed_at', always=True)
    def set_completed_time(cls, v, values):
        """如果状态为完成，但没有完成时间，则设置当前时间"""
        if values.get('status') == ShoppingListStatus.COMPLETED and v is None:
            return datetime.now()
        return v


class ShoppingListItemBatchUpdate(BaseModel):
    """批量更新购物清单条目的请求模型"""
    item_ids: List[str]
    is_purchased: bool


class ShoppingListGenerateRequest(BaseModel):
    """从菜单计划生成购物清单的请求模型"""
    name: str
    plan_ids: List[str]
    family_id: Optional[str] = None 