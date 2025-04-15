"""
API依赖注入模块
"""

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.database import get_db 