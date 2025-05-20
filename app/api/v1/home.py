"""
首页相关路由模块
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, Query, Depends, HTTPException, status

from app.models.homepage import ContentType, HomeContentResponse
from app.services.homepage import get_swipers, get_featured_recipes, get_popular_recipes, create_swiper, create_card
from app.db.mongodb import get_database, get_collection
from app.api.dependencies import get_current_user
from app.core.response import success_response
from app.core.decorators import api_response

router = APIRouter()


@router.get("/")
@api_response
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
        "welcome": "欢迎使用家宴菜谱系统",
        "swipers": swipers,
        "featured": featured,
        "popular": popular
    }


@router.get("/swipers")
@api_response
async def get_home_swipers():
    """
    获取首页轮播图数据
    
    - 返回轮播图列表
    """
    # 示例数据
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
        },
        {
            "id": "3",
            "image": "/static/home/banner3.png",
            "link": "/pages/recipe/detail/index?id=123"
        }
    ]
    
    return swipers


@router.get("/cards")
@api_response
async def get_home_cards():
    """
    获取首页卡片数据
    
    - 返回首页卡片列表
    """
    # 示例数据
    cards = [
        {
            "id": "1",
            "title": "每日精选",
            "image": "/static/home/card1.png",
            "description": "今日推荐美食",
            "link": "/pages/recipe/list/index?category=recommended"
        },
        {
            "id": "2",
            "title": "流行食谱",
            "image": "/static/home/card2.png",
            "description": "热门菜品排行",
            "link": "/pages/recipe/list/index?category=popular"
        },
        {
            "id": "3",
            "title": "快手简餐",
            "image": "/static/home/card3.png",
            "description": "15分钟搞定",
            "link": "/pages/recipe/list/index?category=quick"
        },
        {
            "id": "4",
            "title": "家庭聚餐",
            "image": "/static/home/card4.png",
            "description": "适合多人分享",
            "link": "/pages/recipe/list/index?category=family"
        }
    ]
    
    return cards


@router.get("/recommended")
@api_response
async def get_recommended_recipes(current_user: Optional[Dict[str, Any]] = Depends(get_current_user)):
    """
    获取推荐菜谱
    
    - 可选授权: Bearer Token (有授权则提供个性化推荐)
    - 返回推荐菜谱列表
    """
    # 示例数据 - 根据用户喜好或通用推荐
    is_personalized = current_user is not None
    
    recommended = [
        {
            "id": "101",
            "name": "香煎三文鱼",
            "image": "/static/recipes/salmon.png",
            "cookTime": 20,
            "difficulty": "中等",
            "tags": ["高蛋白", "低碳水"]
        },
        {
            "id": "102",
            "name": "西红柿炒鸡蛋",
            "image": "/static/recipes/tomato_egg.png",
            "cookTime": 10,
            "difficulty": "简单",
            "tags": ["家常菜", "快手菜"]
        },
        {
            "id": "103",
            "name": "红烧排骨",
            "image": "/static/recipes/pork_ribs.png",
            "cookTime": 45,
            "difficulty": "中等",
            "tags": ["经典菜", "肉类"]
        }
    ]
    
    return {
        "recipes": recommended,
        "is_personalized": is_personalized
    }


@router.get("/seasonal")
@api_response
async def get_seasonal_ingredients():
    """
    获取应季食材
    
    - 返回当季食材列表
    """
    # 获取当前月份 (1-12)
    current_month = datetime.now().month
    
    # 根据月份确定季节
    season = ""
    if 3 <= current_month <= 5:
        season = "春季"
    elif 6 <= current_month <= 8:
        season = "夏季"
    elif 9 <= current_month <= 11:
        season = "秋季"
    else:
        season = "冬季"
    
    # 示例数据 - 根据季节提供不同食材
    ingredients = {
        "春季": [
            {"id": "1", "name": "春笋", "image": "/static/ingredients/bamboo.png", "description": "鲜嫩多汁"},
            {"id": "2", "name": "菠菜", "image": "/static/ingredients/spinach.png", "description": "富含铁质"},
            {"id": "3", "name": "荠菜", "image": "/static/ingredients/shepherds_purse.png", "description": "清香可口"}
        ],
        "夏季": [
            {"id": "4", "name": "西瓜", "image": "/static/ingredients/watermelon.png", "description": "消暑解渴"},
            {"id": "5", "name": "黄瓜", "image": "/static/ingredients/cucumber.png", "description": "清脆爽口"},
            {"id": "6", "name": "茄子", "image": "/static/ingredients/eggplant.png", "description": "紫色营养"}
        ],
        "秋季": [
            {"id": "7", "name": "南瓜", "image": "/static/ingredients/pumpkin.png", "description": "香甜可口"},
            {"id": "8", "name": "栗子", "image": "/static/ingredients/chestnut.png", "description": "香糯滋补"},
            {"id": "9", "name": "莲藕", "image": "/static/ingredients/lotus_root.png", "description": "清脆爽口"}
        ],
        "冬季": [
            {"id": "10", "name": "白萝卜", "image": "/static/ingredients/radish.png", "description": "清甜脆嫩"},
            {"id": "11", "name": "橘子", "image": "/static/ingredients/orange.png", "description": "酸甜可口"},
            {"id": "12", "name": "白菜", "image": "/static/ingredients/cabbage.png", "description": "清甜爽口"}
        ]
    }
    
    return {
        "season": season,
        "ingredients": ingredients.get(season, [])
    }


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