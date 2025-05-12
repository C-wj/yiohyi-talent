import asyncio
from datetime import datetime
from bson import ObjectId
from app.db.mongodb import connect_to_mongo, get_collection

async def create_sample_comments():
    print("连接到 MongoDB...")
    await connect_to_mongo()
    
    # 获取集合
    recipes_collection = get_collection("recipes")
    comments_collection = get_collection("comments")
    
    # 示例评论数据
    sample_comments = [
        {
            "recipe_id": "681dc66f64f725c88d76041d",  # 红烧肉的ID
            "user_id": "67fe0d5c9d553803eed861e0",
            "content": "这个红烧肉的做法很正宗，肥而不腻，口感很好！",
            "rating": 5,
            "images": [],
            "likes": 12,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "recipe_id": "681dc66f64f725c88d76041d",
            "user_id": "67fe0d5c9d553803eed861e0",
            "content": "按照步骤做出来效果很好，家人都说好吃！",
            "rating": 4,
            "images": [],
            "likes": 8,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        },
        {
            "recipe_id": "681dc66f64f725c88d76041d",
            "user_id": "67fe0d5c9d553803eed861e0",
            "content": "建议可以加入一些八角增加香味，整体很不错！",
            "rating": 5,
            "images": [],
            "likes": 5,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    ]
    
    try:
        # 检查菜谱是否存在
        recipe = await recipes_collection.find_one({"_id": ObjectId("681dc66f64f725c88d76041d")})
        if not recipe:
            print("菜谱不存在，请先创建菜谱")
            return
        
        # 删除现有评论
        await comments_collection.delete_many({"recipe_id": "681dc66f64f725c88d76041d"})
        
        # 插入评论
        await comments_collection.insert_many(sample_comments)
        print(f"成功创建 {len(sample_comments)} 条示例评论")
        
        # 更新菜谱的评论统计
        total_rating = sum(comment["rating"] for comment in sample_comments)
        avg_rating = total_rating / len(sample_comments)
        
        await recipes_collection.update_one(
            {"_id": ObjectId("681dc66f64f725c88d76041d")},
            {
                "$set": {
                    "stats.commentCount": len(sample_comments),
                    "stats.ratingAvg": avg_rating,
                    "stats.ratingCount": len(sample_comments)
                }
            }
        )
        
        # 确认创建成功
        comments = await comments_collection.find({"recipe_id": "681dc66f64f725c88d76041d"}).to_list(length=10)
        print(f"\n数据库中现有 {len(comments)} 条评论：")
        for comment in comments:
            print(f"评论ID: {comment.get('_id')}, 内容: {comment.get('content')[:20]}...")
            
    except Exception as e:
        print(f"创建示例评论时出错: {str(e)}")

if __name__ == "__main__":
    asyncio.run(create_sample_comments()) 