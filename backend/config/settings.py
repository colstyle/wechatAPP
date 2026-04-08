# -*- coding: utf-8 -*-
"""
配置文件
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "小时光租衣舍"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库配置
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "527000"
    DB_NAME: str = "Celestial_db"

    # JWT配置
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    # 微信小程序配置
    WECHAT_APP_ID: str = "your-wechat-app-id"
    WECHAT_APP_SECRET: str = "your-wechat-app-secret"

    # 微信支付配置 (测试商户号)
    WECHAT_PAY_APP_ID: str = "test-app-id"
    WECHAT_PAY_MCH_ID: str = "test-mch-id"
    WECHAT_PAY_PRIVATE_KEY: str = "test-private-key"
    WECHAT_PAY_SERIAL_NO: str = "test-serial-no"
    WECHAT_PAY_APIV3_PRIVATE_KEY: str = "test-apiv3-key"

    # TTLock配置
    TTLOCK_CLIENT_ID: str = "test-client-id"
    TTLOCK_CLIENT_SECRET: str = "test-client-secret"
    TTLOCK_ACCESS_TOKEN: str = "test-access-token"

    # CORS配置
    CORS_ORIGINS: list = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# 数据库连接URL
DATABASE_URL = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8mb4"
