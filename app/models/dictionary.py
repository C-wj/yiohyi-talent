from datetime import datetime
from bson import ObjectId
from app.utils.mongodb_utils import get_db, serialize_document

class Dictionary:
    """字典配置模型"""
    
    def __init__(self):
        self.db = get_db()
        self.collection = self.db.dictionaries
        
    def create_dict_type(self, data):
        """创建字典类型"""
        dict_type = {
            "name": data.get("name"),
            "code": data.get("code"),
            "description": data.get("description"),
            "status": data.get("status", 1),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = self.collection.insert_one(dict_type)
        dict_type["_id"] = result.inserted_id
        return serialize_document(dict_type)
    
    def create_dict_item(self, type_code, data):
        """创建字典项"""
        dict_item = {
            "type_code": type_code,
            "label": data.get("label"),
            "value": data.get("value"),
            "sort": data.get("sort", 0),
            "status": data.get("status", 1),
            "remark": data.get("remark"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = self.db.dict_items.insert_one(dict_item)
        dict_item["_id"] = result.inserted_id
        return serialize_document(dict_item)
    
    def get_dict_by_code(self, code):
        """根据代码获取字典类型及其项"""
        dict_type = self.collection.find_one({"code": code})
        if not dict_type:
            return None
        
        dict_type = serialize_document(dict_type)
        
        # 获取字典项
        items = list(self.db.dict_items.find({
            "type_code": code,
            "status": 1
        }).sort("sort", 1))
        
        dict_type["items"] = [serialize_document(item) for item in items]
        return dict_type
    
    def get_all_dict_types(self):
        """获取所有字典类型"""
        types = list(self.collection.find())
        return [serialize_document(t) for t in types] 