import asyncio
from app.db.mongodb import connect_to_mongo
from app.services.homepage import get_swipers


async def test_get_swipers():
    print("连接到 MongoDB...")
    await connect_to_mongo()
    
    print("调用 get_swipers 函数...")
    swipers = await get_swipers()
    
    print(f"get_swipers 函数返回 {len(swipers)} 个结果")
    for i, swiper in enumerate(swipers):
        print(f"轮播图 {i+1}:")
        print(f"  ID: {swiper.get('id') or swiper.get('_id')}")
        print(f"  标题: {swiper.get('title')}")
        print(f"  图片: {swiper.get('image_url')}")
        print(f"  类型: {swiper.get('type')}")


if __name__ == "__main__":
    asyncio.run(test_get_swipers()) 