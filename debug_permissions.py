#!/usr/bin/env python3
"""
调试脚本：检查用户权限获取
"""

import asyncio
import logging
from app.db.mongodb import get_database, connect_to_mongo
from app.services.rbac_service import UserRoleService
from app.models.rbac import PERMISSIONS_COLLECTION
from app.utils.mongodb_utils import MongoDBUtils

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)

async def debug_user_permissions():
    """调试用户权限获取"""
    try:
        # 连接数据库
        await connect_to_mongo()
        db = get_database()
        
        user_id = "682d6fa6a234817b168c9be5"
        
        print(f"调试用户 {user_id} 的权限获取...")
        
        # 手动实现权限获取逻辑
        print("\n手动实现权限获取逻辑...")
        try:
            # 获取用户角色
            user_roles = await UserRoleService.get_user_roles(user_id)
            print(f"获取到用户角色: {len(user_roles)}")
            
            # 收集所有权限ID
            permission_ids = set()
            for role in user_roles:
                print(f"处理角色: {role['name']}, 激活状态: {role.get('is_active', True)}")
                if role.get("is_active", True):  # 默认为True，因为角色表中可能没有这个字段
                    permissions = role.get("permissions", [])
                    print(f"角色权限数量: {len(permissions)}")
                    permission_ids.update(permissions)
            
            print(f"总权限ID数量: {len(permission_ids)}")
            
            # 获取权限详情
            permission_collection = db[PERMISSIONS_COLLECTION]
            
            permission_codes = []
            for perm_id in permission_ids:
                try:
                    print(f"获取权限详情: {perm_id}")
                    perm = await MongoDBUtils.get_document_by_id(permission_collection, perm_id)
                    if perm:
                        print(f"  权限: {perm['name']} ({perm['code']}), 激活: {perm.get('is_active', True)}")
                        if perm.get("is_active", True):
                            permission_codes.append(perm["code"])
                    else:
                        print(f"  权限ID {perm_id} 不存在")
                except Exception as e:
                    print(f"  获取权限 {perm_id} 时出错: {str(e)}")
            
            print(f"最终权限代码列表: {permission_codes}")
            print(f"权限代码数量: {len(permission_codes)}")
            
            # 测试特定权限
            test_permission = "role:read"
            has_permission = test_permission in permission_codes
            print(f"用户是否有 {test_permission} 权限: {has_permission}")
            
            return permission_codes
            
        except Exception as e:
            print(f"手动权限获取失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
        
    except Exception as e:
        print(f"调试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_user_permissions()) 