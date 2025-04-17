from fastapi import APIRouter, HTTPException, status
from typing import List

from app.schemas.services import ServiceResponse

router = APIRouter()


@router.get("/", response_model=dict)
async def get_service_list():
    """
    获取服务列表
    
    - 返回系统提供的服务列表
    """
    try:
        # 创建服务列表数据
        services = [
            {
                "id": "1",
                "name": "菜谱分享",
                "icon": "share",
                "description": "分享您的菜谱与朋友",
                "url": "/pages/recipe/share",
                "status": "active"
            },
            {
                "id": "2",
                "name": "膳食计划",
                "icon": "calendar",
                "description": "规划家庭一周膳食",
                "url": "/pages/meal-plan/index",
                "status": "active"
            },
            {
                "id": "3",
                "name": "营养分析",
                "icon": "chart",
                "description": "了解每道菜谱的营养成分",
                "url": "/pages/nutrition/analysis",
                "status": "active"
            },
            {
                "id": "4",
                "name": "厨师咨询",
                "icon": "chat",
                "description": "向专业厨师寻求建议",
                "url": "/pages/consultation/chef",
                "status": "coming-soon"
            }
        ]
        
        return {"code": 200, "data": {"service": services}}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取服务列表失败: {str(e)}"
        ) 