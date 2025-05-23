#!/usr/bin/env python3
"""
测试脚本：检查用户关键权限
"""

import os
import asyncio
import sys
from app.db.mongodb import connect_to_mongo
from app.services.rbac_service import UserRoleService

async def check_user_permissions():
    """检查用户关键权限"""
    try:
        # 设置环境
        os.environ['APP_ENV'] = 'development'
        
        # 连接数据库
        await connect_to_mongo()
        
        user_id = "682d6fa6a234817b168c9be5"
        print(f"检查用户 {user_id} 的关键权限...")
        
        # 关键权限列表
        key_permissions = [
            "menu:read", "role:read", "permission:read", 
            "user_role:read", "user_permission:read",
            "role:create", "role:update", "role:delete"
        ]
        
        all_permissions = await UserRoleService.get_user_permissions(user_id)
        print(f"用户权限列表: {all_permissions}")
        print(f"权限数量: {len(all_permissions)}")
        
        # 检查关键权限
        for perm in key_permissions:
            has_perm = await UserRoleService.check_permission(user_id, perm)
            print(f"权限 {perm}: {'✓' if has_perm else '✗'}")
        
    except Exception as e:
        print(f"检查失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_user_permissions()) 