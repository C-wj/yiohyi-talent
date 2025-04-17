from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from pymongo.collection import Collection

from app.core.config import settings
from app.db.mongodb import get_collection

router = APIRouter(
    prefix="/home",
    tags=["home"],
    responses={404: {"description": "Not found"}},
)

@router.get("/swipers")
async def get_swipers():
    """获取首页轮播图数据"""
    # 实际环境中应该从数据库获取
    swipers = [
        {
            "id": "1", 
            "image": "/static/home/banner1.png",
            "link": "/pages/recipe/list/index?tag=推荐"
        },
        {
            "id": "2", 
            "image": "/static/home/banner2.png",
            "link": "/pages/recipe/list/index?tag=新品"
        }
    ]
    
    return {"code": 200, "msg": "success", "data": swipers}

@router.get("/cards")
async def get_cards():
    """获取首页卡片数据"""
    # 实际环境中应该从数据库获取
    cards = [
        {
            "id": "card1",
            "title": "今日推荐",
            "image": "/static/home/card0.png",
            "link": "/pages/recipe/detail/index?id=rec1"
        },
        {
            "id": "card2",
            "title": "热门菜谱",
            "image": "/static/home/card1.png",
            "link": "/pages/recipe/list/index?sort=popular"
        }
    ]
    
    return {"code": 200, "msg": "success", "data": cards}
