import asyncio
from app.db.mongodb import connect_to_mongo, get_collection

async def list_users():
    await connect_to_mongo()
    users_collection = get_collection("users")
    users = await users_collection.find({}).to_list(length=100)
    print(f"共找到 {len(users)} 个用户：")
    for user in users:
        uid = str(user.get("_id"))
        nickname = user.get("profile", {}).get("nickname", "无昵称")
        print(f"_id: {uid}  昵称: {nickname}")

if __name__ == "__main__":
    asyncio.run(list_users()) 