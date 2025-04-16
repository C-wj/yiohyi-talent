import os
from pathlib import Path
from typing import List, Optional, Union, Dict, Any

from pydantic import validator, AnyHttpUrl
from pydantic import BaseSettings


class Settings(BaseSettings):
    # 基本配置
    APP_NAME: str = "家宴微信小程序后台服务"
    APP_VERSION: str = "0.1.0"
    # development, testing, production
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    API_PREFIX: str = "/api/v1"
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    ALLOWED_HOSTS: List[str] = ["*"]
    CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = ["*"]
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    
    # 数据库配置
    MONGODB_URI: str
    MONGODB_DB_NAME: str
    MONGODB_MIN_POOL_SIZE: int = 10
    MONGODB_MAX_POOL_SIZE: int = 100
    
    # Redis配置
    REDIS_URI: Optional[str] = None
    REDIS_PASSWORD: Optional[str] = None
    
    # JWT配置
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # 微信小程序配置
    WECHAT_MINI_APP_ID: str
    WECHAT_MINI_APP_SECRET: str
    
    # 文件存储配置
    UPLOAD_DIR: Path = Path("static/uploads")
    # 10MB
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]
    # local, oss, cos
    UPLOADS_PROVIDER: str = "local"
    
    # 阿里云OSS配置
    OSS_ACCESS_KEY: Optional[str] = None
    OSS_SECRET_KEY: Optional[str] = None
    OSS_BUCKET: Optional[str] = None
    OSS_ENDPOINT: Optional[str] = None
    OSS_DOMAIN: Optional[str] = None
    
    # 腾讯云COS配置
    COS_SECRET_ID: Optional[str] = None
    COS_SECRET_KEY: Optional[str] = None
    COS_REGION: Optional[str] = None
    COS_BUCKET: Optional[str] = None
    
    # Celery配置
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_DIR: Path = Path("logs")
    SENTRY_DSN: Optional[str] = None
    
    # 安全配置
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: str = "200/minute"
    
    @validator("UPLOAD_DIR", "LOG_DIR")
    def validate_paths(cls, v: Union[str, Path]) -> Path:
        # 确保路径存在
        path = Path(v) if isinstance(v, str) else v
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @validator("CORS_ORIGINS")
    def validate_cors_origins(cls, v: List[str]) -> List[str]:
        if v == ["*"]:
            return v
        parsed_origins = []
        for origin in v:
            if isinstance(origin, str) and not origin.startswith(("http://", "https://")):
                parsed_origins.append(f"http://{origin}")
            else:
                parsed_origins.append(origin)
        return parsed_origins
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# 加载配置并创建单例实例
settings = Settings()

# 确保关键目录存在
for dir_path in [settings.UPLOAD_DIR, settings.LOG_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)