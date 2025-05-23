"""
RBAC (Role-Based Access Control) 服务层
提供角色、权限、菜单的管理功能
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, status

from app.db.mongodb import get_database
from app.models.rbac import (
    Role, Permission, Menu, UserRole,
    RoleType, PermissionType, MenuType, MenuStatus,
    ROLES_COLLECTION, PERMISSIONS_COLLECTION, MENUS_COLLECTION, USER_ROLES_COLLECTION,
    RoleCreateRequest, RoleUpdateRequest,
    PermissionCreateRequest, PermissionUpdateRequest,
    MenuCreateRequest, MenuUpdateRequest,
    UserRoleAssignRequest
)
from app.utils.mongodb_utils import MongoDBUtils

logger = logging.getLogger(__name__)


class RoleService:
    """角色服务"""
    
    @staticmethod
    async def create_role(role_data: RoleCreateRequest, creator_id: str) -> Dict[str, Any]:
        """创建角色"""
        try:
            db = get_database()
            role_collection = db[ROLES_COLLECTION]
            
            # 检查角色代码是否已存在
            existing_role = await role_collection.find_one({"code": role_data.code})
            if existing_role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"角色代码 {role_data.code} 已存在"
                )
            
            # 创建角色数据
            role_dict = role_data.dict()
            role_dict["created_by"] = creator_id
            
            return await MongoDBUtils.create_document(role_collection, role_dict)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"创建角色失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建角色失败"
            )
    
    @staticmethod
    async def get_role_by_id(role_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取角色"""
        try:
            db = get_database()
            role_collection = db[ROLES_COLLECTION]
            return await MongoDBUtils.get_document_by_id(role_collection, role_id)
        except Exception as e:
            logger.error(f"获取角色失败: {str(e)}")
            return None
    
    @staticmethod
    async def get_role_by_code(role_code: str) -> Optional[Dict[str, Any]]:
        """根据代码获取角色"""
        try:
            db = get_database()
            role_collection = db[ROLES_COLLECTION]
            role = await role_collection.find_one({"code": role_code})
            return MongoDBUtils.serialize_document(role) if role else None
        except Exception as e:
            logger.error(f"获取角色失败: {str(e)}")
            return None
    
    @staticmethod
    async def update_role(role_id: str, update_data: RoleUpdateRequest) -> Optional[Dict[str, Any]]:
        """更新角色"""
        try:
            db = get_database()
            role_collection = db[ROLES_COLLECTION]
            
            # 检查角色是否存在
            if not await MongoDBUtils.document_exists(role_collection, role_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="角色不存在"
                )
            
            # 过滤空值
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            
            return await MongoDBUtils.update_document(role_collection, role_id, update_dict)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"更新角色失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新角色失败"
            )
    
    @staticmethod
    async def delete_role(role_id: str) -> bool:
        """删除角色"""
        try:
            db = get_database()
            role_collection = db[ROLES_COLLECTION]
            user_role_collection = db[USER_ROLES_COLLECTION]
            
            # 检查是否有用户使用此角色
            user_role_count = await user_role_collection.count_documents({"role_id": role_id})
            if user_role_count > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该角色正在被用户使用，无法删除"
                )
            
            return await MongoDBUtils.delete_document(role_collection, role_id)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"删除角色失败: {str(e)}")
            return False
    
    @staticmethod
    async def list_roles(
        skip: int = 0, 
        limit: int = 100, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """获取角色列表"""
        try:
            db = get_database()
            role_collection = db[ROLES_COLLECTION]
            
            query_filters = filters or {}
            sort_criteria = [("sort_order", 1), ("created_at", -1)]
            
            return await MongoDBUtils.get_documents_batch(
                role_collection, query_filters, skip, limit, sort_criteria
            )
        except Exception as e:
            logger.error(f"获取角色列表失败: {str(e)}")
            return []
    
    @staticmethod
    async def get_role_permissions(role_id: str) -> List[Dict[str, Any]]:
        """获取角色的权限列表"""
        try:
            role = await RoleService.get_role_by_id(role_id)
            if not role:
                return []
            
            permission_ids = role.get("permissions", [])
            if not permission_ids:
                return []
            
            db = get_database()
            permission_collection = db[PERMISSIONS_COLLECTION]
            
            # 批量获取权限信息
            permissions = []
            for perm_id in permission_ids:
                perm = await MongoDBUtils.get_document_by_id(permission_collection, perm_id)
                if perm:
                    permissions.append(perm)
            
            return permissions
        except Exception as e:
            logger.error(f"获取角色权限失败: {str(e)}")
            return []


class PermissionService:
    """权限服务"""
    
    @staticmethod
    async def create_permission(perm_data: PermissionCreateRequest, creator_id: str) -> Dict[str, Any]:
        """创建权限"""
        try:
            db = get_database()
            permission_collection = db[PERMISSIONS_COLLECTION]
            
            # 检查权限代码是否已存在
            existing_perm = await permission_collection.find_one({"code": perm_data.code})
            if existing_perm:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"权限代码 {perm_data.code} 已存在"
                )
            
            # 创建权限数据
            perm_dict = perm_data.dict()
            perm_dict["created_by"] = creator_id
            
            return await MongoDBUtils.create_document(permission_collection, perm_dict)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"创建权限失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建权限失败"
            )
    
    @staticmethod
    async def get_permission_by_id(perm_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取权限"""
        try:
            db = get_database()
            permission_collection = db[PERMISSIONS_COLLECTION]
            return await MongoDBUtils.get_document_by_id(permission_collection, perm_id)
        except Exception as e:
            logger.error(f"获取权限失败: {str(e)}")
            return None
    
    @staticmethod
    async def update_permission(perm_id: str, update_data: PermissionUpdateRequest) -> Optional[Dict[str, Any]]:
        """更新权限"""
        try:
            db = get_database()
            permission_collection = db[PERMISSIONS_COLLECTION]
            
            # 检查权限是否存在
            if not await MongoDBUtils.document_exists(permission_collection, perm_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="权限不存在"
                )
            
            # 过滤空值
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            
            return await MongoDBUtils.update_document(permission_collection, perm_id, update_dict)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"更新权限失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新权限失败"
            )
    
    @staticmethod
    async def delete_permission(perm_id: str) -> bool:
        """删除权限"""
        try:
            db = get_database()
            permission_collection = db[PERMISSIONS_COLLECTION]
            role_collection = db[ROLES_COLLECTION]
            
            # 检查是否有角色使用此权限
            role_count = await role_collection.count_documents({"permissions": perm_id})
            if role_count > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该权限正在被角色使用，无法删除"
                )
            
            return await MongoDBUtils.delete_document(permission_collection, perm_id)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"删除权限失败: {str(e)}")
            return False
    
    @staticmethod
    async def list_permissions(
        skip: int = 0, 
        limit: int = 100, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """获取权限列表"""
        try:
            db = get_database()
            permission_collection = db[PERMISSIONS_COLLECTION]
            
            query_filters = filters or {}
            sort_criteria = [("resource", 1), ("action", 1)]
            
            return await MongoDBUtils.get_documents_batch(
                permission_collection, query_filters, skip, limit, sort_criteria
            )
        except Exception as e:
            logger.error(f"获取权限列表失败: {str(e)}")
            return []


class MenuService:
    """菜单服务"""
    
    @staticmethod
    async def create_menu(menu_data: MenuCreateRequest, creator_id: str) -> Dict[str, Any]:
        """创建菜单"""
        try:
            db = get_database()
            menu_collection = db[MENUS_COLLECTION]
            
            # 检查父菜单是否存在
            if menu_data.parent_id:
                parent_menu = await MongoDBUtils.get_document_by_id(menu_collection, menu_data.parent_id)
                if not parent_menu:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="父菜单不存在"
                    )
            
            # 创建菜单数据
            menu_dict = menu_data.dict()
            menu_dict["created_by"] = creator_id
            
            return await MongoDBUtils.create_document(menu_collection, menu_dict)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"创建菜单失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="创建菜单失败"
            )
    
    @staticmethod
    async def get_menu_by_id(menu_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取菜单"""
        try:
            db = get_database()
            menu_collection = db[MENUS_COLLECTION]
            return await MongoDBUtils.get_document_by_id(menu_collection, menu_id)
        except Exception as e:
            logger.error(f"获取菜单失败: {str(e)}")
            return None
    
    @staticmethod
    async def update_menu(menu_id: str, update_data: MenuUpdateRequest) -> Optional[Dict[str, Any]]:
        """更新菜单"""
        try:
            db = get_database()
            menu_collection = db[MENUS_COLLECTION]
            
            # 检查菜单是否存在
            if not await MongoDBUtils.document_exists(menu_collection, menu_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="菜单不存在"
                )
            
            # 检查父菜单是否存在
            if update_data.parent_id:
                parent_menu = await MongoDBUtils.get_document_by_id(menu_collection, update_data.parent_id)
                if not parent_menu:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="父菜单不存在"
                    )
            
            # 过滤空值
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            
            return await MongoDBUtils.update_document(menu_collection, menu_id, update_dict)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"更新菜单失败: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新菜单失败"
            )
    
    @staticmethod
    async def delete_menu(menu_id: str) -> bool:
        """删除菜单"""
        try:
            db = get_database()
            menu_collection = db[MENUS_COLLECTION]
            
            # 检查是否有子菜单
            child_count = await menu_collection.count_documents({"parent_id": menu_id})
            if child_count > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该菜单下有子菜单，无法删除"
                )
            
            return await MongoDBUtils.delete_document(menu_collection, menu_id)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"删除菜单失败: {str(e)}")
            return False
    
    @staticmethod
    async def list_menus(
        skip: int = 0, 
        limit: int = 100, 
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """获取菜单列表"""
        try:
            db = get_database()
            menu_collection = db[MENUS_COLLECTION]
            
            query_filters = filters or {}
            sort_criteria = [("sort_order", 1), ("created_at", 1)]
            
            return await MongoDBUtils.get_documents_batch(
                menu_collection, query_filters, skip, limit, sort_criteria
            )
        except Exception as e:
            logger.error(f"获取菜单列表失败: {str(e)}")
            return []
    
    @staticmethod
    async def get_menu_tree(user_permissions: List[str] = None) -> List[Dict[str, Any]]:
        """获取菜单树结构"""
        try:
            db = get_database()
            menu_collection = db[MENUS_COLLECTION]
            
            # 获取所有启用的菜单
            query_filters = {"status": MenuStatus.ACTIVE}
            all_menus = await MongoDBUtils.get_documents_batch(
                menu_collection, query_filters, 0, 1000, [("sort_order", 1)]
            )
            
            # 如果提供了用户权限，过滤菜单
            if user_permissions:
                filtered_menus = []
                for menu in all_menus:
                    if not menu.get("permission_code") or menu["permission_code"] in user_permissions:
                        filtered_menus.append(menu)
                all_menus = filtered_menus
            
            # 构建树结构
            menu_dict = {menu["id"]: menu for menu in all_menus}
            tree = []
            
            for menu in all_menus:
                menu["children"] = []
                if not menu.get("parent_id"):
                    tree.append(menu)
                else:
                    parent = menu_dict.get(menu["parent_id"])
                    if parent:
                        parent["children"].append(menu)
            
            return tree
        except Exception as e:
            logger.error(f"获取菜单树失败: {str(e)}")
            return []


class UserRoleService:
    """用户角色服务"""
    
    @staticmethod
    async def assign_roles(assign_data: UserRoleAssignRequest, assigner_id: str) -> bool:
        """分配用户角色"""
        try:
            db = get_database()
            user_role_collection = db[USER_ROLES_COLLECTION]
            
            # 删除用户现有角色
            await user_role_collection.delete_many({"user_id": assign_data.user_id})
            
            # 分配新角色
            for role_id in assign_data.role_ids:
                user_role_data = {
                    "user_id": assign_data.user_id,
                    "role_id": role_id,
                    "assigned_by": assigner_id,
                    "expires_at": assign_data.expires_at
                }
                await MongoDBUtils.create_document(user_role_collection, user_role_data)
            
            return True
        except Exception as e:
            logger.error(f"分配用户角色失败: {str(e)}")
            return False
    
    @staticmethod
    async def get_user_roles(user_id: str) -> List[Dict[str, Any]]:
        """获取用户角色"""
        try:
            db = get_database()
            user_role_collection = db[USER_ROLES_COLLECTION]
            role_collection = db[ROLES_COLLECTION]
            
            # 获取用户角色关联
            user_roles = await MongoDBUtils.get_documents_batch(
                user_role_collection, {"user_id": user_id, "is_active": True}
            )
            
            # 获取角色详情
            roles = []
            for user_role in user_roles:
                role = await MongoDBUtils.get_document_by_id(role_collection, user_role["role_id"])
                if role:
                    roles.append(role)
            
            return roles
        except Exception as e:
            logger.error(f"获取用户角色失败: {str(e)}")
            return []
    
    @staticmethod
    async def get_user_permissions(user_id: str) -> List[str]:
        """获取用户权限代码列表"""
        try:
            # 获取用户角色
            user_roles = await UserRoleService.get_user_roles(user_id)
            
            # 收集所有权限ID
            permission_ids = set()
            for role in user_roles:
                if role.get("is_active"):
                    permission_ids.update(role.get("permissions", []))
            
            # 获取权限详情
            db = get_database()
            permission_collection = db[PERMISSIONS_COLLECTION]
            
            permission_codes = []
            for perm_id in permission_ids:
                perm = await MongoDBUtils.get_document_by_id(permission_collection, perm_id)
                if perm and perm.get("is_active"):
                    permission_codes.append(perm["code"])
            
            return permission_codes
        except Exception as e:
            logger.error(f"获取用户权限失败: {str(e)}")
            return []
    
    @staticmethod
    async def check_permission(user_id: str, permission_code: str) -> bool:
        """检查用户是否有指定权限"""
        try:
            user_permissions = await UserRoleService.get_user_permissions(user_id)
            return permission_code in user_permissions
        except Exception as e:
            logger.error(f"检查用户权限失败: {str(e)}")
            return False
    
    @staticmethod
    async def check_user_permission(user_id: str, permission_code: str) -> bool:
        """检查用户是否有指定权限（别名方法）"""
        return await UserRoleService.check_permission(user_id, permission_code) 