import asyncio
import json
from datetime import datetime
from bson import ObjectId
from bson.json_util import dumps
from app.db.mongodb import connect_to_mongo, get_collection
from app.services.homepage import ContentType, HOME_CONTENT_COLLECTION


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


async def debug_query():
    print("连接到 MongoDB...")
    await connect_to_mongo()
    
    print("获取 home_contents 集合...")
    content_collection = get_collection(HOME_CONTENT_COLLECTION)
    
    print("直接查询所有内容...")
    all_contents = await content_collection.find({}).to_list(length=100)
    print(f"总共发现 {len(all_contents)} 条内容")
    
    # 按类型分组显示
    types = {}
    for content in all_contents:
        content_type = content.get('type', 'unknown')
        if content_type not in types:
            types[content_type] = 0
        types[content_type] += 1
    
    print("内容类型统计:")
    for t, count in types.items():
        print(f"- {t}: {count}条")
    
    print("\n查询轮播图内容...")
    query = {"type": ContentType.SWIPER.value}
    swipers = await content_collection.find(query).to_list(length=10)
    print(f"查询到 {len(swipers)} 条轮播图内容")
    
    if len(swipers) > 0:
        print("\n第一条轮播图内容:")
        print(json.dumps(swipers[0], indent=2, cls=JSONEncoder))
    else:
        print("\n!!!未找到轮播图内容!!!")
        # 检查类型枚举值
        print(f"ContentType.SWIPER.value = '{ContentType.SWIPER.value}'")
        
        # 检查类型字段在数据库中的存储情况
        print("\n检查数据库中的'type'字段值...")
        pipeline = [
            {"$group": {"_id": "$type", "count": {"$sum": 1}}}
        ]
        type_stats = await content_collection.aggregate(pipeline).to_list(length=100)
        print("数据库中的type字段统计:")
        for stat in type_stats:
            print(f"- '{stat['_id']}': {stat['count']}条")
        
        # 尝试更宽松的查询
        print("\n尝试使用正则表达式查询...")
        regex_query = {"type": {"$regex": "swiper", "$options": "i"}}
        regex_results = await content_collection.find(regex_query).to_list(length=10)
        print(f"正则查询结果: {len(regex_results)}条")
        
        if len(regex_results) > 0:
            print("正则查询找到的第一条结果:")
            print(json.dumps(regex_results[0], indent=2, cls=JSONEncoder))
    
    # 测试initialize_default_swipers逻辑
    print("\n测试直接查询首页内容的逻辑...")
    from app.models.homepage import SwiperCreate
    from app.services.homepage import create_swiper
    
    print("创建测试轮播图...")
    swiper_data = {
        "title": "测试轮播图",
        "image_url": "/static/home/test.png",
        "description": "测试数据",
        "tags": [{"text": "测试", "theme": "primary"}],
        "sort_order": 999
    }
    swiper = SwiperCreate(**swiper_data)
    
    try:
        result = await create_swiper(swiper, "test_user")
        print("轮播图创建结果:")
        print(json.dumps(result, indent=2, cls=JSONEncoder))
        
        # 再次查询
        print("\n再次查询轮播图内容...")
        swipers_after = await content_collection.find({"type": ContentType.SWIPER.value}).to_list(length=20)
        print(f"查询到 {len(swipers_after)} 条轮播图内容")
    except Exception as e:
        print(f"创建轮播图时出错: {str(e)}")


if __name__ == "__main__":
    asyncio.run(debug_query()) 