import asyncio
from bson import ObjectId
from app.db.mongodb import connect_to_mongo, get_collection

async def list_recipes():
    print("连接到 MongoDB...")
    await connect_to_mongo()
    
    # 获取菜谱集合
    recipes_collection = get_collection("recipes")
    
    # 查询所有菜谱
    recipes = await recipes_collection.find({}).to_list(length=10)
    
    if not recipes:
        print("未找到任何菜谱")
        return
    
    print(f"找到 {len(recipes)} 个菜谱：")
    for recipe in recipes:
        recipe_id = recipe.get("_id")
        title = recipe.get("title", "无标题")
        if isinstance(recipe_id, ObjectId):
            recipe_id = str(recipe_id)
        print(f"ID: {recipe_id}, 标题: {title}")
    
    # 检查特定ID
    specific_id = "681dc66f64f725c88d76041d"
    try:
        obj_id = ObjectId(specific_id)
        specific_recipe = await recipes_collection.find_one({"_id": obj_id})
        if specific_recipe:
            print(f"\n找到ID为 {specific_id} 的菜谱: {specific_recipe.get('title')}")
        else:
            print(f"\n未找到ID为 {specific_id} 的菜谱")
    except Exception as e:
        print(f"\n检查特定ID时出错: {str(e)}")

if __name__ == "__main__":
    asyncio.run(list_recipes()) 