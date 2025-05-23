"""
RBAC数据初始化脚本
创建默认的角色、权限和菜单数据
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any

from app.db.mongodb import get_database, connect_to_mongo
from app.models.rbac import (
    RoleType, PermissionType, MenuType, MenuStatus,
    ROLES_COLLECTION, PERMISSIONS_COLLECTION, MENUS_COLLECTION
)
from app.utils.mongodb_utils import MongoDBUtils

logger = logging.getLogger(__name__)


class RBACDataInitializer:
    """RBAC数据初始化器"""
    
    def __init__(self):
        self.db = None
        self.permissions_map = {}  # 权限代码到ID的映射
        self.roles_map = {}        # 角色代码到ID的映射
        self.menus_map = {}        # 菜单名称到ID的映射
    
    async def initialize(self):
        """初始化数据库连接"""
        from app.db.mongodb import connect_to_mongo
        
        # 先连接到MongoDB
        await connect_to_mongo()
        self.db = get_database()
    
    async def init_permissions(self) -> Dict[str, str]:
        """初始化权限数据"""
        logger.info("开始初始化权限数据...")
        
        permissions_data = [
            # 角色管理权限
            {"name": "创建角色", "code": "role:create", "resource": "role", "action": PermissionType.WRITE, "description": "创建新角色"},
            {"name": "查看角色", "code": "role:read", "resource": "role", "action": PermissionType.READ, "description": "查看角色信息"},
            {"name": "更新角色", "code": "role:update", "resource": "role", "action": PermissionType.WRITE, "description": "更新角色信息"},
            {"name": "删除角色", "code": "role:delete", "resource": "role", "action": PermissionType.DELETE, "description": "删除角色"},
            
            # 权限管理权限
            {"name": "创建权限", "code": "permission:create", "resource": "permission", "action": PermissionType.WRITE, "description": "创建新权限"},
            {"name": "查看权限", "code": "permission:read", "resource": "permission", "action": PermissionType.READ, "description": "查看权限信息"},
            {"name": "更新权限", "code": "permission:update", "resource": "permission", "action": PermissionType.WRITE, "description": "更新权限信息"},
            {"name": "删除权限", "code": "permission:delete", "resource": "permission", "action": PermissionType.DELETE, "description": "删除权限"},
            
            # 菜单管理权限
            {"name": "创建菜单", "code": "menu:create", "resource": "menu", "action": PermissionType.WRITE, "description": "创建新菜单"},
            {"name": "查看菜单", "code": "menu:read", "resource": "menu", "action": PermissionType.READ, "description": "查看菜单信息"},
            {"name": "更新菜单", "code": "menu:update", "resource": "menu", "action": PermissionType.WRITE, "description": "更新菜单信息"},
            {"name": "删除菜单", "code": "menu:delete", "resource": "menu", "action": PermissionType.DELETE, "description": "删除菜单"},
            
            # 用户角色管理权限
            {"name": "分配用户角色", "code": "user_role:assign", "resource": "user_role", "action": PermissionType.WRITE, "description": "分配用户角色"},
            {"name": "查看用户角色", "code": "user_role:read", "resource": "user_role", "action": PermissionType.READ, "description": "查看用户角色"},
            {"name": "查看用户权限", "code": "user_permission:read", "resource": "user_permission", "action": PermissionType.READ, "description": "查看用户权限"},
            
            # 用户管理权限
            {"name": "创建用户", "code": "user:create", "resource": "user", "action": PermissionType.WRITE, "description": "创建新用户"},
            {"name": "查看用户", "code": "user:read", "resource": "user", "action": PermissionType.READ, "description": "查看用户信息"},
            {"name": "更新用户", "code": "user:update", "resource": "user", "action": PermissionType.WRITE, "description": "更新用户信息"},
            {"name": "删除用户", "code": "user:delete", "resource": "user", "action": PermissionType.DELETE, "description": "删除用户"},
            
            # 系统配置权限
            {"name": "系统配置", "code": "system:config", "resource": "system", "action": PermissionType.WRITE, "description": "系统配置管理"},
            {"name": "字典管理", "code": "dict:manage", "resource": "dict", "action": PermissionType.WRITE, "description": "字典数据管理"},
            {"name": "公告管理", "code": "notice:manage", "resource": "notice", "action": PermissionType.WRITE, "description": "公告管理"},
            
            # 内容管理权限
            {"name": "菜谱管理", "code": "recipe:manage", "resource": "recipe", "action": PermissionType.WRITE, "description": "菜谱内容管理"},
            {"name": "订单管理", "code": "order:manage", "resource": "order", "action": PermissionType.WRITE, "description": "订单管理"},
            
            # 统计分析权限
            {"name": "数据统计", "code": "stats:view", "resource": "stats", "action": PermissionType.READ, "description": "查看数据统计"},
            {"name": "报表导出", "code": "report:export", "resource": "report", "action": PermissionType.READ, "description": "导出报表数据"},
        ]
        
        permission_collection = self.db[PERMISSIONS_COLLECTION]
        
        for perm_data in permissions_data:
            # 检查权限是否已存在
            existing = await permission_collection.find_one({"code": perm_data["code"]})
            if existing:
                self.permissions_map[perm_data["code"]] = str(existing["_id"])
                logger.info(f"权限 {perm_data['code']} 已存在，跳过创建")
                continue
            
            # 创建权限
            created_perm = await MongoDBUtils.create_document(permission_collection, perm_data)
            self.permissions_map[perm_data["code"]] = created_perm["id"]
            logger.info(f"创建权限: {perm_data['name']} ({perm_data['code']})")
        
        logger.info(f"权限初始化完成，共创建/确认 {len(permissions_data)} 个权限")
        return self.permissions_map
    
    async def init_roles(self) -> Dict[str, str]:
        """初始化角色数据"""
        logger.info("开始初始化角色数据...")
        
        # 定义角色及其权限
        roles_data = [
            {
                "name": "超级管理员",
                "code": "super_admin",
                "type": RoleType.SUPER_ADMIN,
                "description": "系统超级管理员，拥有所有权限",
                "is_default": False,
                "sort_order": 1,
                "permissions": list(self.permissions_map.values())  # 拥有所有权限
            },
            {
                "name": "管理员",
                "code": "admin",
                "type": RoleType.ADMIN,
                "description": "系统管理员，拥有大部分管理权限",
                "is_default": False,
                "sort_order": 2,
                "permissions": [
                    self.permissions_map.get("role:read"),
                    self.permissions_map.get("permission:read"),
                    self.permissions_map.get("menu:read"),
                    self.permissions_map.get("user_role:assign"),
                    self.permissions_map.get("user_role:read"),
                    self.permissions_map.get("user_permission:read"),
                    self.permissions_map.get("user:read"),
                    self.permissions_map.get("user:update"),
                    self.permissions_map.get("recipe:manage"),
                    self.permissions_map.get("order:manage"),
                    self.permissions_map.get("stats:view"),
                    self.permissions_map.get("report:export"),
                ]
            },
            {
                "name": "会员",
                "code": "member",
                "type": RoleType.MEMBER,
                "description": "付费会员，享有高级功能",
                "is_default": False,
                "sort_order": 3,
                "permissions": [
                    self.permissions_map.get("recipe:manage"),
                    self.permissions_map.get("stats:view"),
                ]
            },
            {
                "name": "普通用户",
                "code": "user",
                "type": RoleType.USER,
                "description": "普通用户，基础功能权限",
                "is_default": True,
                "sort_order": 4,
                "permissions": []  # 基础权限，无特殊权限
            }
        ]
        
        role_collection = self.db[ROLES_COLLECTION]
        
        for role_data in roles_data:
            # 过滤掉None值的权限
            role_data["permissions"] = [p for p in role_data["permissions"] if p is not None]
            
            # 检查角色是否已存在
            existing = await role_collection.find_one({"code": role_data["code"]})
            if existing:
                self.roles_map[role_data["code"]] = str(existing["_id"])
                logger.info(f"角色 {role_data['code']} 已存在，跳过创建")
                continue
            
            # 创建角色
            created_role = await MongoDBUtils.create_document(role_collection, role_data)
            self.roles_map[role_data["code"]] = created_role["id"]
            logger.info(f"创建角色: {role_data['name']} ({role_data['code']})")
        
        logger.info(f"角色初始化完成，共创建/确认 {len(roles_data)} 个角色")
        return self.roles_map
    
    async def init_menus(self) -> Dict[str, str]:
        """初始化菜单数据"""
        logger.info("开始初始化菜单数据...")
        
        # 定义菜单结构
        menus_data = [
            # 主菜单
            {
                "name": "dashboard",
                "title": "仪表盘",
                "path": "/dashboard",
                "component": "Dashboard",
                "icon": "dashboard",
                "type": MenuType.MENU,
                "sort_order": 1,
                "permission_code": None,  # 所有用户都可以访问
                "meta": {"title": "仪表盘", "icon": "dashboard"}
            },
            
            # 系统管理
            {
                "name": "system",
                "title": "系统管理",
                "path": "/system",
                "component": "Layout",
                "icon": "system",
                "type": MenuType.MENU,
                "sort_order": 2,
                "permission_code": "system:config",
                "meta": {"title": "系统管理", "icon": "system"}
            },
            
            # 用户管理
            {
                "name": "user-management",
                "title": "用户管理",
                "path": "/system/users",
                "component": "UserManagement",
                "icon": "user",
                "type": MenuType.MENU,
                "sort_order": 1,
                "permission_code": "user:read",
                "meta": {"title": "用户管理", "icon": "user"},
                "parent": "system"
            },
            
            # 角色管理
            {
                "name": "role-management",
                "title": "角色管理",
                "path": "/system/roles",
                "component": "RoleManagement",
                "icon": "role",
                "type": MenuType.MENU,
                "sort_order": 2,
                "permission_code": "role:read",
                "meta": {"title": "角色管理", "icon": "role"},
                "parent": "system"
            },
            
            # 权限管理
            {
                "name": "permission-management",
                "title": "权限管理",
                "path": "/system/permissions",
                "component": "PermissionManagement",
                "icon": "permission",
                "type": MenuType.MENU,
                "sort_order": 3,
                "permission_code": "permission:read",
                "meta": {"title": "权限管理", "icon": "permission"},
                "parent": "system"
            },
            
            # 菜单管理
            {
                "name": "menu-management",
                "title": "菜单管理",
                "path": "/system/menus",
                "component": "MenuManagement",
                "icon": "menu",
                "type": MenuType.MENU,
                "sort_order": 4,
                "permission_code": "menu:read",
                "meta": {"title": "菜单管理", "icon": "menu"},
                "parent": "system"
            },
            
            # 字典管理
            {
                "name": "dict-management",
                "title": "字典管理",
                "path": "/system/dict",
                "component": "DictManagement",
                "icon": "dict",
                "type": MenuType.MENU,
                "sort_order": 5,
                "permission_code": "dict:manage",
                "meta": {"title": "字典管理", "icon": "dict"},
                "parent": "system"
            },
            
            # 公告管理
            {
                "name": "notice-management",
                "title": "公告管理",
                "path": "/system/notices",
                "component": "NoticeManagement",
                "icon": "notice",
                "type": MenuType.MENU,
                "sort_order": 6,
                "permission_code": "notice:manage",
                "meta": {"title": "公告管理", "icon": "notice"},
                "parent": "system"
            },
            
            # 内容管理
            {
                "name": "content",
                "title": "内容管理",
                "path": "/content",
                "component": "Layout",
                "icon": "content",
                "type": MenuType.MENU,
                "sort_order": 3,
                "permission_code": "recipe:manage",
                "meta": {"title": "内容管理", "icon": "content"}
            },
            
            # 菜谱管理
            {
                "name": "recipe-management",
                "title": "菜谱管理",
                "path": "/content/recipes",
                "component": "RecipeManagement",
                "icon": "recipe",
                "type": MenuType.MENU,
                "sort_order": 1,
                "permission_code": "recipe:manage",
                "meta": {"title": "菜谱管理", "icon": "recipe"},
                "parent": "content"
            },
            
            # 订单管理
            {
                "name": "order-management",
                "title": "订单管理",
                "path": "/content/orders",
                "component": "OrderManagement",
                "icon": "order",
                "type": MenuType.MENU,
                "sort_order": 2,
                "permission_code": "order:manage",
                "meta": {"title": "订单管理", "icon": "order"},
                "parent": "content"
            },
            
            # 统计分析
            {
                "name": "analytics",
                "title": "统计分析",
                "path": "/analytics",
                "component": "Layout",
                "icon": "analytics",
                "type": MenuType.MENU,
                "sort_order": 4,
                "permission_code": "stats:view",
                "meta": {"title": "统计分析", "icon": "analytics"}
            },
            
            # 数据统计
            {
                "name": "data-stats",
                "title": "数据统计",
                "path": "/analytics/stats",
                "component": "DataStats",
                "icon": "stats",
                "type": MenuType.MENU,
                "sort_order": 1,
                "permission_code": "stats:view",
                "meta": {"title": "数据统计", "icon": "stats"},
                "parent": "analytics"
            },
            
            # 报表导出
            {
                "name": "report-export",
                "title": "报表导出",
                "path": "/analytics/reports",
                "component": "ReportExport",
                "icon": "report",
                "type": MenuType.MENU,
                "sort_order": 2,
                "permission_code": "report:export",
                "meta": {"title": "报表导出", "icon": "report"},
                "parent": "analytics"
            }
        ]
        
        menu_collection = self.db[MENUS_COLLECTION]
        
        # 第一轮：创建所有菜单（不设置parent_id）
        for menu_data in menus_data:
            parent_name = menu_data.pop("parent", None)
            
            # 检查菜单是否已存在
            existing = await menu_collection.find_one({"name": menu_data["name"]})
            if existing:
                self.menus_map[menu_data["name"]] = str(existing["_id"])
                logger.info(f"菜单 {menu_data['name']} 已存在，跳过创建")
                continue
            
            # 创建菜单
            created_menu = await MongoDBUtils.create_document(menu_collection, menu_data)
            self.menus_map[menu_data["name"]] = created_menu["id"]
            logger.info(f"创建菜单: {menu_data['title']} ({menu_data['name']})")
        
        # 第二轮：设置父子关系
        for menu_data in menus_data:
            parent_name = None
            # 重新获取parent信息（因为在第一轮中被pop了）
            for original_menu in menus_data:
                if original_menu["name"] == menu_data["name"]:
                    # 这里需要重新定义menus_data或者用其他方式获取parent信息
                    break
        
        # 重新处理父子关系
        parent_child_map = {
            "user-management": "system",
            "role-management": "system",
            "permission-management": "system",
            "menu-management": "system",
            "dict-management": "system",
            "notice-management": "system",
            "recipe-management": "content",
            "order-management": "content",
            "data-stats": "analytics",
            "report-export": "analytics"
        }
        
        for child_name, parent_name in parent_child_map.items():
            if child_name in self.menus_map and parent_name in self.menus_map:
                child_id = self.menus_map[child_name]
                parent_id = self.menus_map[parent_name]
                
                # 更新子菜单的parent_id
                await menu_collection.update_one(
                    {"_id": MongoDBUtils.to_object_id(child_id)},
                    {"$set": {"parent_id": parent_id, "updated_at": datetime.utcnow()}}
                )
                logger.info(f"设置菜单父子关系: {child_name} -> {parent_name}")
        
        logger.info(f"菜单初始化完成，共创建/确认 {len(menus_data)} 个菜单")
        return self.menus_map
    
    async def run(self):
        """运行初始化流程"""
        try:
            await self.initialize()
            
            logger.info("开始RBAC数据初始化...")
            
            # 1. 初始化权限
            await self.init_permissions()
            
            # 2. 初始化角色
            await self.init_roles()
            
            # 3. 初始化菜单
            await self.init_menus()
            
            logger.info("RBAC数据初始化完成！")
            
            # 输出统计信息
            logger.info(f"权限数量: {len(self.permissions_map)}")
            logger.info(f"角色数量: {len(self.roles_map)}")
            logger.info(f"菜单数量: {len(self.menus_map)}")
            
        except Exception as e:
            logger.error(f"RBAC数据初始化失败: {str(e)}")
            raise


async def main():
    """主函数"""
    logging.basicConfig(level=logging.INFO)
    
    initializer = RBACDataInitializer()
    await initializer.run()


if __name__ == "__main__":
    asyncio.run(main()) 