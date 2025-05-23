"""
RBAC (Role-Based Access Control) 相关模型
包括角色、权限、菜单等数据模型
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from bson import ObjectId

# 集合名称常量
ROLES_COLLECTION = "roles"
PERMISSIONS_COLLECTION = "permissions"
MENUS_COLLECTION = "menus"
ROLE_PERMISSIONS_COLLECTION = "role_permissions"
USER_ROLES_COLLECTION = "user_roles"


class RoleType(str, Enum):
    """角色类型枚举"""
    SUPER_ADMIN = "super_admin"      # 超级管理员
    ADMIN = "admin"                  # 管理员
    MEMBER = "member"                # 会员
    USER = "user"                    # 普通用户


class PermissionType(str, Enum):
    """权限类型枚举"""
    READ = "read"                    # 读取权限
    WRITE = "write"                  # 写入权限
    DELETE = "delete"                # 删除权限
    EXECUTE = "execute"              # 执行权限


class MenuType(str, Enum):
    """菜单类型枚举"""
    MENU = "menu"                    # 菜单
    BUTTON = "button"                # 按钮
    API = "api"                      # API接口


class MenuStatus(str, Enum):
    """菜单状态枚举"""
    ACTIVE = "active"                # 启用
    INACTIVE = "inactive"            # 禁用


# 权限模型
class Permission(BaseModel):
    """权限模型"""
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    name: str                        # 权限名称
    code: str                        # 权限代码
    description: Optional[str] = None # 权限描述
    resource: str                    # 资源标识
    action: PermissionType           # 操作类型
    is_active: bool = True           # 是否启用
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        collection = PERMISSIONS_COLLECTION
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# 角色模型
class Role(BaseModel):
    """角色模型"""
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    name: str                        # 角色名称
    code: str                        # 角色代码
    type: RoleType                   # 角色类型
    description: Optional[str] = None # 角色描述
    is_active: bool = True           # 是否启用
    is_default: bool = False         # 是否默认角色
    sort_order: int = 0              # 排序
    permissions: List[str] = Field(default_factory=list)  # 权限ID列表
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        collection = ROLES_COLLECTION
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# 菜单模型
class Menu(BaseModel):
    """菜单模型"""
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    name: str                        # 菜单名称
    title: str                       # 菜单标题
    path: Optional[str] = None       # 路由路径
    component: Optional[str] = None  # 组件路径
    icon: Optional[str] = None       # 图标
    type: MenuType = MenuType.MENU   # 菜单类型
    parent_id: Optional[str] = None  # 父菜单ID
    sort_order: int = 0              # 排序
    is_hidden: bool = False          # 是否隐藏
    is_cache: bool = True            # 是否缓存
    is_affix: bool = False           # 是否固定标签
    status: MenuStatus = MenuStatus.ACTIVE  # 状态
    permission_code: Optional[str] = None    # 权限代码
    redirect: Optional[str] = None   # 重定向路径
    meta: Dict[str, Any] = Field(default_factory=dict)  # 元数据
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        collection = MENUS_COLLECTION
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# 用户角色关联模型
class UserRole(BaseModel):
    """用户角色关联模型"""
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str                     # 用户ID
    role_id: str                     # 角色ID
    assigned_by: str                 # 分配者ID
    assigned_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None  # 过期时间
    is_active: bool = True           # 是否启用
    
    class Config:
        collection = USER_ROLES_COLLECTION
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


# 请求模型
class RoleCreateRequest(BaseModel):
    """角色创建请求"""
    name: str
    code: str
    type: RoleType
    description: Optional[str] = None
    is_active: bool = True
    is_default: bool = False
    sort_order: int = 0
    permissions: List[str] = Field(default_factory=list)


class RoleUpdateRequest(BaseModel):
    """角色更新请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    sort_order: Optional[int] = None
    permissions: Optional[List[str]] = None


class PermissionCreateRequest(BaseModel):
    """权限创建请求"""
    name: str
    code: str
    description: Optional[str] = None
    resource: str
    action: PermissionType
    is_active: bool = True


class PermissionUpdateRequest(BaseModel):
    """权限更新请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[PermissionType] = None
    is_active: Optional[bool] = None


class MenuCreateRequest(BaseModel):
    """菜单创建请求"""
    name: str
    title: str
    path: Optional[str] = None
    component: Optional[str] = None
    icon: Optional[str] = None
    type: MenuType = MenuType.MENU
    parent_id: Optional[str] = None
    sort_order: int = 0
    is_hidden: bool = False
    is_cache: bool = True
    is_affix: bool = False
    status: MenuStatus = MenuStatus.ACTIVE
    permission_code: Optional[str] = None
    redirect: Optional[str] = None
    meta: Dict[str, Any] = Field(default_factory=dict)


class MenuUpdateRequest(BaseModel):
    """菜单更新请求"""
    name: Optional[str] = None
    title: Optional[str] = None
    path: Optional[str] = None
    component: Optional[str] = None
    icon: Optional[str] = None
    type: Optional[MenuType] = None
    parent_id: Optional[str] = None
    sort_order: Optional[int] = None
    is_hidden: Optional[bool] = None
    is_cache: Optional[bool] = None
    is_affix: Optional[bool] = None
    status: Optional[MenuStatus] = None
    permission_code: Optional[str] = None
    redirect: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


class UserRoleAssignRequest(BaseModel):
    """用户角色分配请求"""
    user_id: str
    role_ids: List[str]
    expires_at: Optional[datetime] = None


# 响应模型
class RoleResponse(BaseModel):
    """角色响应模型"""
    id: str
    name: str
    code: str
    type: RoleType
    description: Optional[str] = None
    is_active: bool
    is_default: bool
    sort_order: int
    permissions: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class MenuResponse(BaseModel):
    """菜单响应模型"""
    id: str
    name: str
    title: str
    path: Optional[str] = None
    component: Optional[str] = None
    icon: Optional[str] = None
    type: MenuType
    parent_id: Optional[str] = None
    sort_order: int
    is_hidden: bool
    is_cache: bool
    is_affix: bool
    status: MenuStatus
    permission_code: Optional[str] = None
    redirect: Optional[str] = None
    meta: Dict[str, Any]
    children: List['MenuResponse'] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class PermissionResponse(BaseModel):
    """权限响应模型"""
    id: str
    name: str
    code: str
    description: Optional[str] = None
    resource: str
    action: PermissionType
    is_active: bool
    created_at: datetime
    updated_at: datetime


# 更新前向引用
MenuResponse.model_rebuild() 