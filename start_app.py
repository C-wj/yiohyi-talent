#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import time
import logging
import importlib
import socket

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("start_app")

# 项目所需的基本依赖
REQUIRED_PACKAGES = [
    "fastapi==0.95.2",
    "uvicorn==0.22.0", 
    "pymongo",
    "motor",
    "python-dotenv",
    "pydantic==1.10.8",
    "python-jose[cryptography]",
    "passlib",
    "python-multipart",
    "beanie",
    "itsdangerous",
    "email-validator",
    "wechatpy",
    "requests"
]

def check_packages():
    """检查并安装所需的Python包"""
    logger.info("检查所需的Python包...")
    
    for package in REQUIRED_PACKAGES:
        package_name = package.split("==")[0]
        try:
            importlib.import_module(package_name.replace('-', '_'))
            logger.info(f"✓ {package} 已安装")
        except ImportError:
            logger.warning(f"× {package} 未安装，正在安装...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            logger.info(f"✓ {package} 安装成功")

def check_mongodb_connection(host, port, username, password, database, timeout=5):
    """检查MongoDB连接是否可用"""
    logger.info(f"检查MongoDB连接 ({host}:{port})...")
    
    # 首先检查主机是否可访问
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        s.close()
        logger.info(f"✓ 连接到MongoDB服务器 {host}:{port} 成功")
    except:
        logger.error(f"× 无法连接到MongoDB服务器 {host}:{port}")
        logger.warning("应用将以有限功能模式启动")
        return False
    
    # 然后尝试导入pymongo并连接数据库
    try:
        import pymongo
        client = pymongo.MongoClient(
            f"mongodb://{username}:{password}@{host}:{port}/{database}",
            serverSelectionTimeoutMS=timeout*1000
        )
        # 验证连接
        client.admin.command('ping')
        logger.info(f"✓ MongoDB认证成功，数据库 {database} 可访问")
        client.close()
        return True
    except Exception as e:
        logger.error(f"× MongoDB连接/认证失败: {str(e)}")
        logger.warning("应用将以有限功能模式启动")
        return False

def start_application(host="0.0.0.0", port=8000):
    """启动FastAPI应用"""
    logger.info(f"正在启动应用 (http://{host}:{port})...")
    
    try:
        # 使用uvicorn直接启动应用，指定host和port
        subprocess.run(
            [
                sys.executable, "-m", "uvicorn", 
                "app.main:app", 
                "--host", host, 
                "--port", str(port),
                "--proxy-headers"  # 启用代理头支持
            ],
            check=True
        )
    except KeyboardInterrupt:
        logger.info("应用已停止")
    except subprocess.CalledProcessError as e:
        logger.error(f"应用启动失败: {str(e)}")
        sys.exit(1)

def parse_mongodb_uri(uri):
    """从MongoDB URI解析连接信息"""
    # 示例: mongodb://username:password@host:port/database
    if not uri.startswith("mongodb://"):
        return None
    
    # 移除mongodb://前缀
    uri = uri[10:]
    
    # 提取认证信息和主机信息
    if "@" in uri:
        auth, host_part = uri.split("@", 1)
        username, password = auth.split(":", 1)
    else:
        host_part = uri
        username = ""
        password = ""
    
    # 提取主机和数据库
    if "/" in host_part:
        host_port, database = host_part.split("/", 1)
    else:
        host_port = host_part
        database = ""
    
    # 提取主机和端口
    if ":" in host_port:
        host, port = host_port.split(":", 1)
        port = int(port)
    else:
        host = host_port
        port = 27017
    
    return {
        "host": host,
        "port": port,
        "username": username,
        "password": password,
        "database": database
    }

def main():
    """主函数"""
    print("\n" + "="*60)
    print("家宴微信小程序后台服务 - 启动程序")
    print("="*60 + "\n")
    
    # 1. 检查并安装依赖包
    try:
        check_packages()
    except Exception as e:
        logger.error(f"安装依赖包失败: {str(e)}")
        sys.exit(1)
    
    # 2. 加载环境变量
    try:
        import dotenv
        dotenv.load_dotenv()
    except Exception as e:
        logger.error(f"加载环境变量失败: {str(e)}")
        sys.exit(1)
    
    # 3. 检查MongoDB连接
    mongodb_uri = os.getenv("MONGODB_URI", "")
    if mongodb_uri:
        conn_info = parse_mongodb_uri(mongodb_uri)
        if conn_info:
            check_mongodb_connection(
                conn_info["host"],
                conn_info["port"],
                conn_info["username"],
                conn_info["password"],
                conn_info["database"]
            )
        else:
            logger.warning(f"无法解析MongoDB URI: {mongodb_uri}")
    else:
        logger.warning("未找到MONGODB_URI环境变量")
    
    # 4. 启动应用
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    logger.info("\n" + "-"*60)
    logger.info(f"正在启动应用，访问地址:")
    logger.info(f"- 主页: http://{host}:{port}/")
    logger.info(f"- API文档: http://{host}:{port}/docs")
    logger.info(f"- 健康检查: http://{host}:{port}/health")
    logger.info("-"*60 + "\n")
    
    start_application(host, port)

if __name__ == "__main__":
    main()