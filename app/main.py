import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

# 导入所有路由模块
from app.api.v1 import auth, users, families, recipes, menu_plans, shopping_lists, ingredients, uploads, home, services
from app.api.v1 import rbac
from app.api.v1.admin import homepage as admin_homepage
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection
from app.db.redis import get_redis, close_redis_connection
# 导入自定义中间件和异常处理
from app.core.exception_handlers import register_exception_handlers


# 应用启动和关闭事件处理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动事件: 尝试连接数据库，但不阻止应用启动
    logging.info("尝试连接到MongoDB...")
    try:
        await connect_to_mongo()
        logging.info("MongoDB连接成功!")
    except Exception as e:
        logging.error(f"MongoDB连接失败: {str(e)}")
        logging.warning("应用将以有限功能模式启动，API可能无法正常工作")
    
    # 尝试连接Redis
    try:
        await get_redis()
    except Exception as e:
        logging.error(f"Redis初始化失败: {str(e)}")
        logging.warning("短信验证码和缓存功能可能无法正常工作")
    
    yield  # 应用运行中
    
    # 关闭事件: 断开数据库连接
    try:
        logging.info("关闭MongoDB连接...")
        await close_mongo_connection()
        logging.info("MongoDB连接已关闭!")
    except Exception as e:
        logging.error(f"关闭MongoDB连接时出错: {str(e)}")
    
    # 关闭Redis连接
    try:
        await close_redis_connection()
    except Exception as e:
        logging.error(f"关闭Redis连接时出错: {str(e)}")


# 初始化FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    description="家宴菜谱微信小程序后台服务API",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)


# 设置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 设置会话中间件
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY
)


# 注册异常处理器
register_exception_handlers(app)


# 添加所有路由
app.include_router(auth.router, prefix=f"{settings.API_PREFIX}/auth", tags=["认证"])
app.include_router(users.router, prefix=f"{settings.API_PREFIX}/users", tags=["用户"])
app.include_router(families.router, prefix=f"{settings.API_PREFIX}/families", tags=["家庭"])
app.include_router(recipes.router, prefix=f"{settings.API_PREFIX}/recipes", tags=["菜谱"])
app.include_router(menu_plans.router, prefix=f"{settings.API_PREFIX}/menu-plans", tags=["点菜系统"])
app.include_router(shopping_lists.router, prefix=f"{settings.API_PREFIX}/shopping-lists", tags=["购物清单"])
app.include_router(ingredients.router, prefix=f"{settings.API_PREFIX}/ingredients", tags=["食材"])
app.include_router(uploads.router, prefix=f"{settings.API_PREFIX}/uploads", tags=["文件上传"])
app.include_router(home.router, prefix=f"{settings.API_PREFIX}/home", tags=["首页"])
app.include_router(services.router, prefix=f"{settings.API_PREFIX}/services", tags=["服务"])
app.include_router(rbac.router, prefix=f"{settings.API_PREFIX}/rbac", tags=["权限管理"])

# 添加管理员路由
app.include_router(
    admin_homepage.router, 
    prefix=f"{settings.API_PREFIX}/admin/homepage", 
    tags=["管理员-首页"]
)


# 健康检查路由
@app.get("/health", tags=["健康检查"])
async def health_check():
    from app.core.response import success_response
    return success_response(data={"status": "healthy", "version": settings.APP_VERSION})


# 根路由
@app.get("/", tags=["根"])
async def root():
    from app.core.response import success_response
    return success_response(
        data={
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs_url": "/docs" if settings.DEBUG else None,
            "environment": settings.APP_ENV
        }
    )


# 直接运行此文件时启动服务器
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host=settings.HOST, 
        port=settings.PORT,
        reload=settings.DEBUG
    ) 