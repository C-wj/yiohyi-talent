"""
RBAC (Role-Based Access Control) API路由
提供角色、权限、菜单管理接口
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer

from app.core.response import success_response, error_response
from app.dependencies.auth import get_current_user
from app.models.rbac import (
    RoleCreateRequest, RoleUpdateRequest, RoleResponse,
    PermissionCreateRequest, PermissionUpdateRequest, PermissionResponse,
    MenuCreateRequest, MenuUpdateRequest, MenuResponse,
    UserRoleAssignRequest
)
from app.services.rbac_service import (
    RoleService, PermissionService, MenuService, UserRoleService
)

# 创建路由器，不再添加重复的前缀
router = APIRouter()

# 权限安全检查
security = HTTPBearer()

# =============== 角色管理接口 ===============

@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """创建角色"""
    # 检查权限
    has_permission = await UserRoleService.check_permission(current_user["id"], "role:create")
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您没有创建角色的权限")
    
    role = await RoleService.create_role(role_data, current_user["id"])
    return success_response(role)


@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(
    skip: int = Query(0, description="分页起始"),
    limit: int = Query(100, description="分页大小"),
    name: Optional[str] = Query(None, description="角色名称"),
    role_type: Optional[str] = Query(None, description="角色类型"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取角色列表"""
    # 检查权限
    has_permission = await UserRoleService.check_permission(current_user["id"], "role:read")
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您没有查看角色的权限")
    
    # 构建过滤条件
    filters = {}
    if name:
        filters["name"] = {"$regex": name, "$options": "i"}
    if role_type:
        filters["type"] = role_type
    
    roles = await RoleService.list_roles(skip, limit, filters)
    return success_response(roles)


@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取角色详情"""
    # 检查权限
    has_permission = await UserRoleService.check_permission(current_user["id"], "role:read")
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您没有查看角色的权限")
    
    role = await RoleService.get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    
    return success_response(role)


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: str,
    update_data: RoleUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """更新角色"""
    # 检查权限
    has_permission = await UserRoleService.check_permission(current_user["id"], "role:update")
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您没有更新角色的权限")
    
    updated_role = await RoleService.update_role(role_id, update_data)
    if not updated_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    
    return success_response(updated_role)


@router.delete("/roles/{role_id}")
async def delete_role(
    role_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """删除角色"""
    # 检查权限
    has_permission = await UserRoleService.check_permission(current_user["id"], "role:delete")
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您没有删除角色的权限")
    
    success = await RoleService.delete_role(role_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在或删除失败")
    
    return success_response({"message": "角色删除成功"})


@router.get("/roles/{role_id}/permissions", response_model=List[PermissionResponse])
async def get_role_permissions(
    role_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取角色权限"""
    # 检查权限
    has_permission = await UserRoleService.check_permission(current_user["id"], "role:read")
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您没有查看角色权限的权限")
    
    role = await RoleService.get_role_by_id(role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    
    permissions = await RoleService.get_role_permissions(role_id)
    return success_response(permissions)


# =============== 权限管理接口 ===============

@router.post("/permissions", response_model=PermissionResponse)
async def create_permission(
    permission_data: PermissionCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """创建权限"""
    # 检查权限
    has_permission = await UserRoleService.check_permission(current_user["id"], "permission:create")
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您没有创建权限的权限")
    
    permission = await PermissionService.create_permission(permission_data, current_user["id"])
    return success_response(permission)


@router.get("/permissions", response_model=List[PermissionResponse])
async def list_permissions(
    skip: int = Query(0, description="分页起始"),
    limit: int = Query(100, description="分页大小"),
    resource: Optional[str] = Query(None, description="资源类型"),
    action: Optional[str] = Query(None, description="操作类型"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取权限列表"""
    # 检查权限
    has_permission = await UserRoleService.check_permission(current_user["id"], "permission:read")
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您没有查看权限的权限")
    
    # 构建过滤条件
    filters = {}
    if resource:
        filters["resource"] = resource
    if action:
        filters["action"] = action
    
    permissions = await PermissionService.list_permissions(skip, limit, filters)
    return success_response(permissions)


@router.get("/permissions/{permission_id}", response_model=PermissionResponse)
async def get_permission(
    permission_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取权限详情"""
    # 检查权限
    has_permission = await UserRoleService.check_permission(current_user["id"], "permission:read")
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您没有查看权限的权限")
    
    permission = await PermissionService.get_permission_by_id(permission_id)
    if not permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="权限不存在")
    
    return success_response(permission)


@router.put("/permissions/{permission_id}", response_model=PermissionResponse)
async def update_permission(
    permission_id: str,
    update_data: PermissionUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """更新权限"""
    # 检查权限
    has_permission = await UserRoleService.check_permission(current_user["id"], "permission:update")
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您没有更新权限的权限")
    
    updated_permission = await PermissionService.update_permission(permission_id, update_data)
    if not updated_permission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="权限不存在")
    
    return success_response(updated_permission)


@router.delete("/permissions/{permission_id}")
async def delete_permission(
    permission_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """删除权限"""
    # 检查权限
    has_permission = await UserRoleService.check_permission(current_user["id"], "permission:delete")
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您没有删除权限的权限")
    
    success = await PermissionService.delete_permission(permission_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="权限不存在或删除失败")
    
    return success_response({"message": "权限删除成功"})


# =============== 菜单管理接口 ===============

@router.post("/menus", response_model=MenuResponse)
async def create_menu(
    menu_data: MenuCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """创建菜单"""
    # 检查权限
    has_permission = await UserRoleService.check_permission(current_user["id"], "menu:create")
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您没有创建菜单的权限")
    
    menu = await MenuService.create_menu(menu_data, current_user["id"])
    return success_response(menu)


@router.get("/menus", response_model=List[MenuResponse])
async def list_menus(
    skip: int = Query(0, description="分页起始"),
    limit: int = Query(100, description="分页大小"),
    menu_type: Optional[str] = Query(None, description="菜单类型"),
    title: Optional[str] = Query(None, description="菜单标题"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取菜单列表"""
    # 检查权限
    has_permission = await UserRoleService.check_permission(current_user["id"], "menu:read")
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您没有查看菜单的权限")
    
    # 构建过滤条件
    filters = {}
    if menu_type:
        filters["type"] = menu_type
    if title:
        filters["title"] = {"$regex": title, "$options": "i"}
    
    menus = await MenuService.list_menus(skip, limit, filters)
    return success_response(menus)


@router.get("/menu-tree", response_model=List[MenuResponse])
async def get_menu_tree(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取菜单树"""
    # 获取用户权限
    user_permissions = await UserRoleService.get_user_permissions(current_user["id"])
    
    # 获取菜单树
    menu_tree = await MenuService.get_menu_tree(user_permissions)
    return success_response(menu_tree)


@router.get("/menus/{menu_id}", response_model=MenuResponse)
async def get_menu(
    menu_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取菜单详情"""
    # 检查权限
    has_permission = await UserRoleService.check_permission(current_user["id"], "menu:read")
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您没有查看菜单的权限")
    
    menu = await MenuService.get_menu_by_id(menu_id)
    if not menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="菜单不存在")
    
    return success_response(menu)


@router.put("/menus/{menu_id}", response_model=MenuResponse)
async def update_menu(
    menu_id: str,
    update_data: MenuUpdateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """更新菜单"""
    # 检查权限
    has_permission = await UserRoleService.check_permission(current_user["id"], "menu:update")
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您没有更新菜单的权限")
    
    updated_menu = await MenuService.update_menu(menu_id, update_data)
    if not updated_menu:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="菜单不存在")
    
    return success_response(updated_menu)


@router.delete("/menus/{menu_id}")
async def delete_menu(
    menu_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """删除菜单"""
    # 检查权限
    has_permission = await UserRoleService.check_permission(current_user["id"], "menu:delete")
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您没有删除菜单的权限")
    
    success = await MenuService.delete_menu(menu_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="菜单不存在或删除失败")
    
    return success_response({"message": "菜单删除成功"})


# =============== 用户角色管理接口 ===============

@router.post("/users/{user_id}/roles")
async def assign_user_roles(
    user_id: str,
    assign_data: UserRoleAssignRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """分配用户角色"""
    # 检查权限
    has_permission = await UserRoleService.check_permission(current_user["id"], "user_role:assign")
    if not has_permission:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您没有分配用户角色的权限")
    
    # 验证用户ID一致性
    if user_id != assign_data.user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户ID不匹配")
    
    success = await UserRoleService.assign_roles(assign_data, current_user["id"])
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="分配角色失败")
    
    return success_response({"message": "角色分配成功"})


@router.get("/users/{user_id}/roles")
async def get_user_roles(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取用户角色"""
    # 检查权限
    has_permission = await UserRoleService.check_permission(current_user["id"], "user_role:read")
    if not has_permission and current_user["id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您没有查看用户角色的权限")
    
    roles = await UserRoleService.get_user_roles(user_id)
    return success_response(roles)


@router.get("/users/{user_id}/permissions")
async def get_user_permissions(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """获取用户权限"""
    # 检查权限
    has_permission = await UserRoleService.check_permission(current_user["id"], "user_permission:read")
    if not has_permission and current_user["id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您没有查看用户权限的权限")
    
    permissions = await UserRoleService.get_user_permissions(user_id)
    return success_response(permissions)


@router.get("/users/{user_id}/has-permission")
async def check_user_permission(
    user_id: str,
    permission: str = Query(..., description="权限代码"),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """检查用户是否有指定权限"""
    # 检查权限
    has_permission = await UserRoleService.check_permission(current_user["id"], "user_permission:read")
    if not has_permission and current_user["id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="您没有查看用户权限的权限")
    
    has_perm = await UserRoleService.check_permission(user_id, permission)
    return success_response({"has_permission": has_perm}) 