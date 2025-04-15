from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from pydantic import BaseModel, Field


class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch" 
    DINNER = "dinner"
    SNACK = "snack"
    OTHER = "other"


class MenuPlanStatus(str, Enum):
    DRAFT = "draft"
    PLANNED = "planned"
    SHOPPING = "shopping"
    COOKING = "cooking"
    COMPLETED = "completed"
    CANCELED = "canceled"


class DishDetail(BaseModel):
    recipeId: str
    title: str
    image: Optional[str] = None
    servings: int = 1
    notes: Optional[str] = None


class Meal(BaseModel):
    type: MealType
    time: Optional[str] = None
    dishes: List[DishDetail] = Field(default_factory=list)


class Collaborator(BaseModel):
    userId: str
    nickname: str
    avatar: Optional[str] = None
    role: str = "viewer"  # "owner", "editor", "viewer"


class SpecialNeed(BaseModel):
    description: str
    forUser: Optional[str] = None  # 用户ID或名称


class MenuPlanModel(BaseModel):
    name: str
    familyId: str
    creatorId: str
    date: datetime
    meals: List[Meal] = Field(default_factory=list)
    guestCount: int = 0
    specialNeeds: List[SpecialNeed] = Field(default_factory=list)
    status: MenuPlanStatus = MenuPlanStatus.DRAFT
    shoppingListId: Optional[str] = None
    collaborators: List[Collaborator] = Field(default_factory=list)
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)
    confirmedAt: Optional[datetime] = None


# API请求响应模型
class MenuPlanCreate(BaseModel):
    name: str
    familyId: str
    date: datetime
    meals: List[Meal] = Field(default_factory=list)
    guestCount: int = 0
    specialNeeds: List[SpecialNeed] = Field(default_factory=list)
    status: MenuPlanStatus = MenuPlanStatus.DRAFT
    collaborators: List[Collaborator] = Field(default_factory=list)


class MenuPlanUpdate(BaseModel):
    name: Optional[str] = None
    date: Optional[datetime] = None
    meals: Optional[List[Meal]] = None
    guestCount: Optional[int] = None
    specialNeeds: Optional[List[SpecialNeed]] = None
    status: Optional[MenuPlanStatus] = None
    collaborators: Optional[List[Collaborator]] = None
    shoppingListId: Optional[str] = None
    confirmedAt: Optional[datetime] = None


class DishAdd(BaseModel):
    recipeId: str
    mealType: MealType
    servings: int = 1
    notes: Optional[str] = None


class MenuPlanResponse(BaseModel):
    id: str
    name: str
    familyId: str
    creatorId: str
    date: datetime
    meals: List[Meal]
    guestCount: int
    specialNeeds: List[SpecialNeed]
    status: MenuPlanStatus
    shoppingListId: Optional[str] = None
    collaborators: List[Collaborator]
    createdAt: datetime
    updatedAt: datetime
    confirmedAt: Optional[datetime] = None


class MenuPlanListParams(BaseModel):
    familyId: Optional[str] = None
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    status: Optional[List[MenuPlanStatus]] = None
    page: int = 1
    pageSize: int = 10 