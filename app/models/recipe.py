from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class RecipeCreator(BaseModel):
    userId: str
    nickname: str
    avatar: Optional[str] = None


class Substitute(BaseModel):
    name: str
    amount: Optional[float] = None
    unit: Optional[str] = None


class Ingredient(BaseModel):
    name: str
    amount: Optional[float] = None
    unit: Optional[str] = None
    category: Optional[str] = None
    optional: bool = False
    substitutes: List[Substitute] = Field(default_factory=list)
    note: Optional[str] = None


class Step(BaseModel):
    stepNumber: int
    description: str
    image: Optional[str] = None
    duration: Optional[int] = None
    tips: Optional[str] = None


class Nutrition(BaseModel):
    calories: Optional[float] = None
    protein: Optional[float] = None
    fat: Optional[float] = None
    carbs: Optional[float] = None
    fiber: Optional[float] = None
    sugar: Optional[float] = None
    sodium: Optional[float] = None
    source: Optional[str] = None


class RecipeStats(BaseModel):
    viewCount: int = 0
    favoriteCount: int = 0
    commentCount: int = 0
    cookCount: int = 0
    ratingAvg: float = 0.0
    ratingCount: int = 0


class RecipeModel(BaseModel):
    title: str
    coverImage: Optional[str] = None
    description: str
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    cuisine: Optional[str] = None
    difficulty: int = 1  # 1-5
    prepTime: int = 0  # 准备时间(分钟)
    cookTime: int = 0  # 烹饪时间(分钟)
    totalTime: int = 0  # 总时间(分钟)
    servings: int = 1  # 份量(人数)
    
    creator: RecipeCreator
    ingredients: List[Ingredient] = Field(default_factory=list)
    steps: List[Step] = Field(default_factory=list)
    nutrition: Optional[Nutrition] = None
    tips: List[str] = Field(default_factory=list)
    
    isPublic: bool = False
    isOrigin: bool = True
    sourceId: Optional[str] = None
    status: str = "draft"  # 'draft','published','deleted'
    
    stats: RecipeStats = Field(default_factory=RecipeStats)
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)


# API请求响应模型
class RecipeCreate(BaseModel):
    title: str
    coverImage: Optional[str] = None
    description: str
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    cuisine: Optional[str] = None
    difficulty: int = 1
    prepTime: int = 0
    cookTime: int = 0
    totalTime: int = 0
    servings: int = 1
    ingredients: List[Ingredient] = Field(default_factory=list)
    steps: List[Step] = Field(default_factory=list)
    nutrition: Optional[Nutrition] = None
    tips: List[str] = Field(default_factory=list)
    isPublic: bool = False


class RecipeUpdate(BaseModel):
    title: Optional[str] = None
    coverImage: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    cuisine: Optional[str] = None
    difficulty: Optional[int] = None
    prepTime: Optional[int] = None
    cookTime: Optional[int] = None
    totalTime: Optional[int] = None
    servings: Optional[int] = None
    ingredients: Optional[List[Ingredient]] = None
    steps: Optional[List[Step]] = None
    nutrition: Optional[Nutrition] = None
    tips: Optional[List[str]] = None
    isPublic: Optional[bool] = None
    status: Optional[str] = None


class RecipeResponse(BaseModel):
    id: str
    title: str
    coverImage: Optional[str] = None
    description: str
    tags: List[str]
    category: Optional[str] = None
    cuisine: Optional[str] = None
    difficulty: int
    prepTime: int
    cookTime: int
    totalTime: int
    servings: int
    creator: RecipeCreator
    ingredients: List[Ingredient]
    steps: List[Step]
    nutrition: Optional[Nutrition] = None
    tips: List[str]
    isPublic: bool
    isOrigin: bool
    sourceId: Optional[str] = None
    status: str
    stats: RecipeStats
    createdAt: datetime
    updatedAt: datetime


class RecipeSearchParams(BaseModel):
    keyword: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    cuisine: Optional[str] = None
    difficulty: Optional[int] = None
    maxTime: Optional[int] = None  # 最大总时间(分钟)
    isPublic: Optional[bool] = None
    creatorId: Optional[str] = None
    page: int = 1
    pageSize: int = 10
    sortBy: str = "createdAt"  # createdAt, popularity, rating
    sortDirection: str = "desc"  # asc, desc 