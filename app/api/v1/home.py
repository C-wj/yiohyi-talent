"""
首页相关路由模块
"""
from typing import List, Dict, Any

from fastapi import APIRouter, Query

from app.models.homepage import ContentType, HomeContentResponse
from app.services.homepage import get_swipers, get_featured_recipes, get_popular_recipes

router = APIRouter()


@router.get("/")
async def get_home_data():
    """
    获取首页数据
    """
    # 获取各种首页内容
    swipers = await get_swipers()
    featured = await get_featured_recipes()
    popular = await get_popular_recipes()
    
    return {
        "status": "success",
        "message": "首页数据获取成功",
        "data": {
            "welcome": "欢迎使用家宴菜谱系统",
            "swipers": swipers,
            "featured": featured,
            "popular": popular
        }
    }


@router.get("/swipers", response_model=List[HomeContentResponse])
async def get_home_swipers(
    limit: int = Query(6, description="返回的轮播图数量")
):
    """
    获取首页轮播图数据
    """
    # 从数据库获取轮播图数据
    swipers = await get_swipers()
    
    # 如果数据库中没有轮播图数据，返回默认数据
    if not swipers:
        # 返回轮播图图片URL列表（静态数据作为备用）
        default_swipers = [
            {
                "id": f"default-swiper-{i}",
                "type": ContentType.SWIPER.value,
                "title": f"默认轮播图 {i+1}",
                "image_url": f"/static/home/swiper{i}.png",
                "description": f"默认轮播图示例 {i+1}"
            } for i in range(min(6, limit))
        ]
        return default_swipers[:limit]
    
    return swipers[:limit]


@router.get("/cards", response_model=List[HomeContentResponse])
async def get_home_cards(
    card_type: str = Query(ContentType.FEATURED.value, description="卡片类型"),
    limit: int = Query(5, description="返回的卡片数量")
):
    """
    获取首页卡片数据
    """
    # 根据卡片类型从数据库获取数据
    if card_type == ContentType.FEATURED.value:
        cards = await get_featured_recipes()
    elif card_type == ContentType.POPULAR.value:
        cards = await get_popular_recipes()
    else:
        cards = []
    
    # 如果数据库中没有卡片数据，返回默认数据
    if not cards:
        # 返回卡片数据列表（静态数据作为备用）
        default_cards = [
            {
                "id": "default-card-0",
                "type": card_type,
                "title": "家常红烧肉",
                "image_url": "/static/home/card0.png",
                "description": "家常红烧肉，肥而不腻",
                "tags": [
                    {"text": "家常菜", "theme": "primary"},
                    {"text": "肉类", "theme": "success"}
                ]
            },
            {
                "id": "default-card-1",
                "type": card_type,
                "title": "清蒸鲈鱼",
                "image_url": "/static/home/card1.png",
                "description": "清蒸鲈鱼，鲜香可口",
                "tags": [
                    {"text": "海鲜", "theme": "primary"},
                    {"text": "低脂", "theme": "success"}
                ]
            },
            {
                "id": "default-card-2",
                "type": card_type,
                "title": "宫保鸡丁",
                "image_url": "/static/home/card2.png",
                "description": "宫保鸡丁，麻辣鲜香",
                "tags": [
                    {"text": "川菜", "theme": "primary"},
                    {"text": "家常菜", "theme": "success"}
                ]
            },
            {
                "id": "default-card-3",
                "type": card_type,
                "title": "番茄炒蛋",
                "image_url": "/static/home/card3.png",
                "description": "番茄炒蛋，酸甜可口",
                "tags": [
                    {"text": "快手菜", "theme": "primary"},
                    {"text": "家常菜", "theme": "success"}
                ]
            },
            {
                "id": "default-card-4",
                "type": card_type,
                "title": "水煮鱼片",
                "image_url": "/static/home/card4.png",
                "description": "水煮鱼片，麻辣鲜香",
                "tags": [
                    {"text": "川菜", "theme": "primary"},
                    {"text": "鱼类", "theme": "success"}
                ]
            }
        ]
        return default_cards[:limit]
    
    return cards[:limit] 