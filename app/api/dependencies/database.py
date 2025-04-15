"""
数据库依赖注入
"""
from app.db.mongodb import get_database

def get_db():
    """
    获取数据库连接
    """
    return get_database() 