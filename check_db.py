import asyncio
from app.db.mongodb import connect_to_mongo, get_collection
from app.models.homepage import ContentType


async def check_swipers():
    print("尝试连接到 MongoDB...")
    try:
        await connect_to_mongo()
        print("MongoDB 连接成功")
        
        collection = get_collection('home_contents')
        print("获取 home_contents 集合")
        
        swipers = await collection.find({'type': 'swiper'}).to_list(length=10)
        print(f'找到 {len(swipers)} 个轮播图数据')
        
        for swiper in swipers:
            print(f"ID: {swiper.get('_id')}, 标题: {swiper.get('title')}, 图片: {swiper.get('image_url')}")
        
        if len(swipers) == 0:
            print("检查 initialize_default_swipers 函数是否被正确调用")
            
            # 检查其他内容类型是否有数据
            featured = await collection.find({'type': 'featured'}).to_list(length=10)
            popular = await collection.find({'type': 'popular'}).to_list(length=10)
            
            print(f'精选内容: {len(featured)} 条')
            print(f'热门内容: {len(popular)} 条')
    except Exception as e:
        print(f"发生错误: {str(e)}")


if __name__ == "__main__":
    asyncio.run(check_swipers()) 