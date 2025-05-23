from datetime import datetime
from bson import ObjectId
from app.utils.mongodb_utils import get_db, serialize_document

class Menu:
    """菜单模型"""
    
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.menus
        
    def create_menu(self, data):
        """创建菜单"""
        menu = {
            "name": data.get("name"),
            "code": data.get("code"),
            "path": data.get("path"),
            "icon": data.get("icon"),
            "parent_id": data.get("parent_id"),  # 父菜单ID
            "sort": data.get("sort", 0),
            "type": data.get("type", "menu"),  # menu: 菜单, button: 按钮
            "permission": data.get("permission"),  # 权限标识
            "component": data.get("component"),  # 前端组件路径
            "visible": data.get("visible", True),
            "status": data.get("status", 1),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = self.collection.insert_one(menu)
        menu["_id"] = result.inserted_id
        return serialize_document(menu)
    
    def get_menu_tree(self, role_code=None):
        """获取菜单树"""
        query = {"status": 1}
        menus = list(self.collection.find(query).sort("sort", 1))
        menus = [serialize_document(menu) for menu in menus]
        
        # 构建树形结构
        return self._build_tree(menus)
    
    def _build_tree(self, menus, parent_id=None):
        """构建树形结构"""
        tree = []
        for menu in menus:
            if menu.get("parent_id") == parent_id:
                children = self._build_tree(menus, menu["id"])
                if children:
                    menu["children"] = children
                tree.append(menu)
        return tree
    
    def get_menus_by_role(self, role_code):
        """根据角色获取菜单"""
        # 如果是超级管理员，返回所有菜单
        if role_code == "super_admin":
            return self.get_menu_tree()
        
        # 其他角色根据权限返回菜单
        from app.models.role import Role
        role_model = Role()
        role = role_model.get_role_by_code(role_code)
        
        if not role:
            return []
        
        menu_ids = role.get("menus", [])
        query = {
            "_id": {"$in": [ObjectId(mid) for mid in menu_ids]},
            "status": 1
        }
        menus = list(self.collection.find(query).sort("sort", 1))
        menus = [serialize_document(menu) for menu in menus]
        
        return self._build_tree(menus)
    
    def update_menu(self, menu_id, data):
        """更新菜单"""
        data["updated_at"] = datetime.utcnow()
        result = self.collection.update_one(
            {"_id": ObjectId(menu_id)},
            {"$set": data}
        )
        return result.modified_count > 0
    
    def delete_menu(self, menu_id):
        """删除菜单"""
        # 检查是否有子菜单
        if self.collection.find_one({"parent_id": menu_id}):
            return False, "存在子菜单，无法删除"
        
        result = self.collection.delete_one({"_id": ObjectId(menu_id)})
        return result.deleted_count > 0, "删除成功"
    
    def init_default_menus(self):
        """初始化默认菜单"""
        default_menus = [
            # 系统管理
            {
                "name": "系统管理",
                "code": "system",
                "path": "/system",
                "icon": "setting",
                "sort": 1,
                "type": "menu"
            },
            {
                "name": "角色管理",
                "code": "role",
                "path": "/system/role",
                "parent_id": None,  # 需要在创建后更新
                "icon": "user-group",
                "sort": 1,
                "type": "menu",
                "component": "system/role/index"
            },
            {
                "name": "菜单管理",
                "code": "menu",
                "path": "/system/menu",
                "parent_id": None,
                "icon": "menu",
                "sort": 2,
                "type": "menu",
                "component": "system/menu/index"
            },
            {
                "name": "字典管理",
                "code": "dict",
                "path": "/system/dict",
                "parent_id": None,
                "icon": "book",
                "sort": 3,
                "type": "menu",
                "component": "system/dict/index"
            },
            {
                "name": "公告管理",
                "code": "announcement",
                "path": "/system/announcement",
                "parent_id": None,
                "icon": "notification",
                "sort": 4,
                "type": "menu",
                "component": "system/announcement/index"
            }
        ]
        
        # 先创建父菜单
        system_menu = None
        for menu_data in default_menus:
            if menu_data["code"] == "system":
                existing = self.collection.find_one({"code": menu_data["code"]})
                if not existing:
                    system_menu = self.create_menu(menu_data)
                else:
                    system_menu = serialize_document(existing)
                break
        
        # 创建子菜单
        if system_menu:
            for menu_data in default_menus:
                if menu_data["code"] != "system":
                    menu_data["parent_id"] = system_menu["id"]
                    existing = self.collection.find_one({"code": menu_data["code"]})
                    if not existing:
                        self.create_menu(menu_data) 