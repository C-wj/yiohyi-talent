import asyncio
import os
import logging
import sys
from bson import ObjectId
from app.db.mongodb import connect_to_mongo, get_collection
from app.services.recipe import get_recipe_by_id


# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)


async def debug_recipe_retrieval():
    logger.info("开始调试菜谱获取")
    
    try:
        # 连接到MongoDB
        logger.info("连接到MongoDB...")
        await connect_to_mongo()
        
        # 查询菜谱
        recipe_id = "681dc66f64f725c88d76041d"
        logger.info(f"尝试获取菜谱ID: {recipe_id}")
        
        # 直接从集合中查询
        logger.info("直接从集合中查询...")
        recipes_collection = get_collection("recipes")
        
        # 打印集合对象
        logger.info(f"获取的集合对象: {recipes_collection}")
        
        try:
            # 尝试转换ObjectId
            logger.info(f"尝试将 {recipe_id} 转换为ObjectId")
            obj_id = ObjectId(recipe_id)
            logger.info(f"转换成功，ObjectId: {obj_id}")
            
            # 直接查询
            logger.info("执行find_one查询...")
            recipe = await recipes_collection.find_one({"_id": obj_id})
            
            if recipe:
                logger.info(f"找到菜谱: {recipe.get('title', '无标题')}")
                logger.info(f"菜谱内容: {recipe}")
            else:
                logger.info(f"未找到ID为 {recipe_id} 的菜谱")
            
        except Exception as e:
            logger.error(f"查询过程中出错: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
        
        # 使用服务函数查询
        logger.info("\n使用get_recipe_by_id服务函数查询...")
        recipe = await get_recipe_by_id(recipe_id)
        
        if recipe:
            logger.info(f"通过服务函数找到菜谱: {recipe.get('title', '无标题')}")
        else:
            logger.info(f"通过服务函数未找到菜谱")
        
    except Exception as e:
        logger.error(f"调试过程中出错: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(debug_recipe_retrieval()) 