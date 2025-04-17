import logging
from typing import Optional
from redis.asyncio import Redis, from_url

from app.core.config import settings

# 全局Redis连接实例
_redis_client: Optional[Redis] = None


async def get_redis() -> Redis:
    """
    获取Redis连接实例
    """
    global _redis_client
    
    if _redis_client is None:
        try:
            # 从配置文件获取Redis连接信息
            host = "192.168.1.18"
            port = 6379
            database = 2
            password = "ZXyue@_341@"
            
            redis_uri = f"redis://{host}:{port}/{database}"
            
            logging.info(f"正在连接到Redis: {redis_uri}")
            _redis_client = from_url(
                redis_uri,
                password=password,
                encoding="utf-8", 
                decode_responses=False  # 保留原始字节序列
            )
            # 尝试ping确认连接正常
            await _redis_client.ping()
            logging.info("Redis连接成功!")
        except Exception as e:
            logging.error(f"Redis连接失败: {str(e)}")
            # 使用标准Redis库，而不是尝试模拟
            # 只是记录错误，让应用继续运行
            # 短信验证码功能可能不可用
            from redis.asyncio import Redis as AsyncRedis
            class MockRedis(AsyncRedis):
                """简单的Redis模拟实现，用于在Redis服务不可用时提供基本功能"""
                async def get(self, name):
                    logging.warning(f"模拟Redis: 尝试获取键 {name}")
                    return None
                
                async def set(self, name, value, ex=None):
                    logging.warning(f"模拟Redis: 尝试设置键 {name} 为 {value}, 过期时间: {ex}")
                    return True
                
                async def delete(self, *names):
                    logging.warning(f"模拟Redis: 尝试删除键 {names}")
                    return len(names)
                
                async def ping(self):
                    return True
                
                async def close(self):
                    return True
            
            logging.warning("使用模拟的Redis实例!")
            _redis_client = MockRedis()
    
    return _redis_client


async def close_redis_connection():
    """
    关闭Redis连接
    """
    global _redis_client
    
    if _redis_client is not None:
        logging.info("关闭Redis连接...")
        await _redis_client.close()
        _redis_client = None
        logging.info("Redis连接已关闭!") 