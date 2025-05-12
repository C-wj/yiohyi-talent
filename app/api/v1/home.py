"""
首页相关路由模块
"""
from typing import List, Dict, Any

from fastapi import APIRouter, Query, Depends

from app.models.homepage import ContentType, HomeContentResponse
from app.services.homepage import get_swipers, get_featured_recipes, get_popular_recipes, create_swiper, create_card
from app.db.mongodb import get_database, get_collection

router = APIRouter()


@router.get("/")
async def get_home_data():
    """
    获取首页数据
    """
    # 直接从数据库查询各种首页内容
    collection = get_collection("home_contents")
    
    # 查询轮播图
    swipers = await collection.find({"type": ContentType.SWIPER.value}).sort("sort_order", 1).to_list(length=6)
    
    # 查询精选推荐
    featured = await collection.find({"type": ContentType.FEATURED.value}).sort("sort_order", 1).to_list(length=5)
    
    # 查询热门内容
    popular = await collection.find({"type": ContentType.POPULAR.value}).sort("sort_order", 1).to_list(length=5)
    
    # 确保数据存在，如果数据库中没有数据，初始化默认数据
    if not swipers:
        await initialize_default_swipers()
        swipers = await collection.find({"type": ContentType.SWIPER.value}).sort("sort_order", 1).to_list(length=6)
    
    if not featured:
        await initialize_default_featured()
        featured = await collection.find({"type": ContentType.FEATURED.value}).sort("sort_order", 1).to_list(length=5)
    
    if not popular:
        await initialize_default_popular()
        popular = await collection.find({"type": ContentType.POPULAR.value}).sort("sort_order", 1).to_list(length=5)
    
    # 处理数据格式，MongoDB的_id需要转为id字段
    for item in swipers + featured + popular:
        if "_id" in item:
            item["id"] = str(item.pop("_id"))
    
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
    # 直接从数据库查询轮播图数据
    collection = get_collection("home_contents")
    swipers = await collection.find({"type": ContentType.SWIPER.value}).sort("sort_order", 1).to_list(length=limit)
    
    # 如果数据库中没有轮播图数据，进行初始化
    if not swipers:
        await initialize_default_swipers()
        swipers = await collection.find({"type": ContentType.SWIPER.value}).sort("sort_order", 1).to_list(length=limit)
    
    # 处理数据格式，MongoDB的_id需要转为id字段
    result = []
    for swiper in swipers:
        # 转换ID字段
        if "_id" in swiper:
            swiper["id"] = str(swiper.pop("_id"))
        
        result.append(swiper)
    
    return result[:limit]


@router.get("/cards", response_model=List[HomeContentResponse])
async def get_home_cards(
    card_type: str = Query(ContentType.FEATURED.value, description="卡片类型"),
    limit: int = Query(5, description="返回的卡片数量")
):
    """
    获取首页卡片数据
    """
    # 直接从数据库查询卡片数据
    collection = get_collection("home_contents")
    
    if card_type == ContentType.FEATURED.value:
        cards = await collection.find({"type": ContentType.FEATURED.value}).sort("sort_order", 1).to_list(length=limit)
        if not cards:
            await initialize_default_featured()
            cards = await collection.find({"type": ContentType.FEATURED.value}).sort("sort_order", 1).to_list(length=limit)
    elif card_type == ContentType.POPULAR.value:
        cards = await collection.find({"type": ContentType.POPULAR.value}).sort("sort_order", 1).to_list(length=limit)
        if not cards:
            await initialize_default_popular()
            cards = await collection.find({"type": ContentType.POPULAR.value}).sort("sort_order", 1).to_list(length=limit)
    else:
        cards = []
    
    # 处理数据格式，MongoDB的_id需要转为id字段
    result = []
    for card in cards:
        # 转换ID字段
        if "_id" in card:
            card["id"] = str(card.pop("_id"))
        
        result.append(card)
    
    return result[:limit]


# 辅助函数，初始化默认数据
async def initialize_default_swipers():
    """初始化默认轮播图数据"""
    admin_id = "system_admin"  # 系统管理员ID
    
    default_swipers = [
        {
            "title": "家常红烧肉",
            "image_url": "/static/home/swiper0.png",
            "description": "家常红烧肉，肥而不腻",
            "tags": [
                {"text": "家常菜", "theme": "primary"},
                {"text": "肉类", "theme": "success"}
            ],
            "sort_order": 0
        },
        {
            "title": "清蒸鲈鱼",
            "image_url": "/static/home/swiper1.png",
            "description": "清蒸鲈鱼，鲜香可口",
            "tags": [
                {"text": "海鲜", "theme": "primary"},
                {"text": "低脂", "theme": "success"}
            ],
            "sort_order": 1
        },
        {
            "title": "宫保鸡丁",
            "image_url": "/static/home/swiper2.png",
            "description": "宫保鸡丁，麻辣鲜香",
            "tags": [
                {"text": "川菜", "theme": "primary"},
                {"text": "家常菜", "theme": "success"}
            ],
            "sort_order": 2
        }
    ]
    
    # 将默认数据插入数据库
    for swiper_data in default_swipers:
        from app.models.homepage import SwiperCreate
        swiper = SwiperCreate(**swiper_data)
        await create_swiper(swiper, admin_id)


async def initialize_default_featured():
    """初始化默认精选菜谱数据"""
    admin_id = "system_admin"  # 系统管理员ID
    
    default_featured = [
        {
            "title": "家常红烧肉",
            "image_url": "/static/home/card0.png",
            "target_id": "default_recipe_1",
            "target_type": "recipe",
            "description": "家常红烧肉，肥而不腻",
            "tags": [
                {"text": "家常菜", "theme": "primary"},
                {"text": "肉类", "theme": "success"}
            ],
            "sort_order": 0
        },
        {
            "title": "清蒸鲈鱼",
            "image_url": "/static/home/card1.png",
            "target_id": "default_recipe_2",
            "target_type": "recipe",
            "description": "清蒸鲈鱼，鲜香可口",
            "tags": [
                {"text": "海鲜", "theme": "primary"},
                {"text": "低脂", "theme": "success"}
            ],
            "sort_order": 1
        },
        {
            "title": "宫保鸡丁",
            "image_url": "/static/home/card2.png",
            "target_id": "default_recipe_3",
            "target_type": "recipe",
            "description": "宫保鸡丁，麻辣鲜香",
            "tags": [
                {"text": "川菜", "theme": "primary"},
                {"text": "家常菜", "theme": "success"}
            ],
            "sort_order": 2
        }
    ]
    
    # 将默认数据插入数据库
    for card_data in default_featured:
        from app.models.homepage import CardCreate, ContentType
        card = CardCreate(**card_data)
        await create_card(card, ContentType.FEATURED, admin_id)


async def initialize_default_popular():
    """初始化默认热门菜谱数据"""
    admin_id = "system_admin"  # 系统管理员ID
    
    default_popular = [
        {
            "title": "番茄炒蛋",
            "image_url": "/static/home/card3.png",
            "target_id": "default_recipe_4",
            "target_type": "recipe",
            "description": "番茄炒蛋，酸甜可口",
            "tags": [
                {"text": "快手菜", "theme": "primary"},
                {"text": "家常菜", "theme": "success"}
            ],
            "sort_order": 0
        },
        {
            "title": "水煮鱼片",
            "image_url": "/static/home/card4.png",
            "target_id": "default_recipe_5",
            "target_type": "recipe",
            "description": "水煮鱼片，麻辣鲜香",
            "tags": [
                {"text": "川菜", "theme": "primary"},
                {"text": "鱼类", "theme": "success"}
            ],
            "sort_order": 1
        }
    ]
    
    # 将默认数据插入数据库
    for card_data in default_popular:
        from app.models.homepage import CardCreate, ContentType
        card = CardCreate(**card_data)
        await create_card(card, ContentType.POPULAR, admin_id) 