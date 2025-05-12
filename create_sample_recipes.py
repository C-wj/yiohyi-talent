import asyncio
from datetime import datetime
from bson import ObjectId
from app.db.mongodb import connect_to_mongo, get_collection

async def create_sample_recipes():
    print("连接到 MongoDB...")
    await connect_to_mongo()
    
    # 获取菜谱集合
    recipes_collection = get_collection("recipes")
    
    # 创建一个示例菜谱
    sample_recipes = [
        {
            "_id": ObjectId("681dc66f64f725c88d76041d"),  # 使用之前尝试访问的ID
            "title": "家常红烧肉",
            "coverImage": "/static/recipes/hongshaorou.jpg",
            "description": "传统家常红烧肉，肥而不腻，口感醇厚",
            "tags": ["家常菜", "肉类", "红烧", "下饭菜"],
            "category": "荤菜",
            "cuisine": "川菜",
            "difficulty": "中等",
            "prepTime": 20,
            "cookTime": 90,
            "totalTime": 110,
            "servings": 4,
            "creator": {
                "userId": "system",
                "nickname": "系统管理员",
                "avatar": "/static/avatars/admin.png"
            },
            "ingredients": [
                {
                    "name": "五花肉",
                    "amount": "500",
                    "unit": "克"
                },
                {
                    "name": "姜",
                    "amount": "3",
                    "unit": "片"
                },
                {
                    "name": "蒜",
                    "amount": "2",
                    "unit": "瓣"
                },
                {
                    "name": "料酒",
                    "amount": "2",
                    "unit": "勺"
                },
                {
                    "name": "生抽",
                    "amount": "3",
                    "unit": "勺"
                },
                {
                    "name": "老抽",
                    "amount": "1",
                    "unit": "勺"
                },
                {
                    "name": "冰糖",
                    "amount": "20",
                    "unit": "克"
                }
            ],
            "steps": [
                {
                    "stepNumber": 1,
                    "description": "将五花肉切成大小均匀的块",
                    "image": "/static/recipes/steps/hongshaorou_1.jpg"
                },
                {
                    "stepNumber": 2,
                    "description": "锅中加入清水，放入五花肉块，加入姜片、料酒，大火煮开，撇去浮沫",
                    "image": "/static/recipes/steps/hongshaorou_2.jpg"
                },
                {
                    "stepNumber": 3,
                    "description": "锅中放少量油，加入冰糖，小火慢慢炒至冰糖融化并呈焦糖色",
                    "image": "/static/recipes/steps/hongshaorou_3.jpg"
                },
                {
                    "stepNumber": 4,
                    "description": "倒入汆烫好的五花肉，快速翻炒上色",
                    "image": "/static/recipes/steps/hongshaorou_4.jpg"
                },
                {
                    "stepNumber": 5,
                    "description": "加入生抽、老抽、料酒，加水没过肉块，大火烧开后转小火慢炖1小时",
                    "image": "/static/recipes/steps/hongshaorou_5.jpg"
                },
                {
                    "stepNumber": 6,
                    "description": "最后收汁，即可出锅",
                    "image": "/static/recipes/steps/hongshaorou_6.jpg"
                }
            ],
            "nutrition": {
                "calories": 450,
                "protein": 22,
                "fat": 36,
                "carbs": 10
            },
            "tips": "可以加入少量八角和桂皮增加香味，收汁时可以加入少量白糖调味。",
            "isPublic": True,
            "isOrigin": True,
            "sourceId": None,
            "status": "published",
            "stats": {
                "viewCount": 0,
                "favoriteCount": 0,
                "commentCount": 0,
                "cookCount": 0,
                "ratingAvg": 0.0,
                "ratingCount": 0
            },
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        },
        {
            "title": "清蒸鲈鱼",
            "coverImage": "/static/recipes/qingzhengluyu.jpg",
            "description": "鲜嫩可口的清蒸鲈鱼，保留鱼的原汁原味",
            "tags": ["海鲜", "蒸菜", "低脂", "家常菜"],
            "category": "荤菜",
            "cuisine": "粤菜",
            "difficulty": "简单",
            "prepTime": 15,
            "cookTime": 20,
            "totalTime": 35,
            "servings": 3,
            "creator": {
                "userId": "system",
                "nickname": "系统管理员",
                "avatar": "/static/avatars/admin.png"
            },
            "ingredients": [
                {
                    "name": "鲈鱼",
                    "amount": "1",
                    "unit": "条"
                },
                {
                    "name": "姜",
                    "amount": "3",
                    "unit": "片"
                },
                {
                    "name": "葱",
                    "amount": "2",
                    "unit": "根"
                },
                {
                    "name": "盐",
                    "amount": "1",
                    "unit": "茶匙"
                },
                {
                    "name": "料酒",
                    "amount": "1",
                    "unit": "勺"
                }
            ],
            "steps": [
                {
                    "stepNumber": 1,
                    "description": "鲈鱼处理干净，在鱼身两面各划几刀",
                    "image": "/static/recipes/steps/luyu_1.jpg"
                },
                {
                    "stepNumber": 2,
                    "description": "鱼身上抹盐，腌制15分钟",
                    "image": "/static/recipes/steps/luyu_2.jpg"
                },
                {
                    "stepNumber": 3,
                    "description": "腌制好的鱼放入盘中，鱼肚内放入姜片和葱段",
                    "image": "/static/recipes/steps/luyu_3.jpg"
                },
                {
                    "stepNumber": 4,
                    "description": "锅内水烧开，放入装有鱼的盘子，蒸10-15分钟",
                    "image": "/static/recipes/steps/luyu_4.jpg"
                },
                {
                    "stepNumber": 5,
                    "description": "取出后撒上葱花，淋上热油和生抽即可",
                    "image": "/static/recipes/steps/luyu_5.jpg"
                }
            ],
            "nutrition": {
                "calories": 180,
                "protein": 28,
                "fat": 6,
                "carbs": 2
            },
            "tips": "用热油淋在葱花上可以使香味更加浓郁。",
            "isPublic": True,
            "isOrigin": True,
            "sourceId": None,
            "status": "published",
            "stats": {
                "viewCount": 0,
                "favoriteCount": 0,
                "commentCount": 0,
                "cookCount": 0,
                "ratingAvg": 0.0,
                "ratingCount": 0
            },
            "createdAt": datetime.now(),
            "updatedAt": datetime.now()
        }
    ]
    
    try:
        # 检查是否已存在该ID的菜谱
        existing = await recipes_collection.find_one({"_id": ObjectId("681dc66f64f725c88d76041d")})
        if existing:
            print(f"ID为 681dc66f64f725c88d76041d 的菜谱已存在: {existing.get('title')}")
        else:
            # 插入菜谱
            await recipes_collection.insert_many(sample_recipes)
            print(f"成功创建 {len(sample_recipes)} 个示例菜谱")
            
            # 确认创建成功
            recipes = await recipes_collection.find({}).to_list(length=10)
            print(f"\n数据库中现有 {len(recipes)} 个菜谱：")
            for recipe in recipes:
                recipe_id = recipe.get("_id")
                title = recipe.get("title", "无标题")
                if isinstance(recipe_id, ObjectId):
                    recipe_id = str(recipe_id)
                print(f"ID: {recipe_id}, 标题: {title}")
    except Exception as e:
        print(f"创建示例菜谱时出错: {str(e)}")

if __name__ == "__main__":
    asyncio.run(create_sample_recipes()) 