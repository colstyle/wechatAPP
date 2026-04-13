# -*- coding: utf-8 -*-
"""
多环境配置文件
通过系统环境变量 APP_ENV 决定加载哪个 .env 文件：
  APP_ENV=dev  (默认) → .env
  APP_ENV=test         → .env.test
  APP_ENV=prod         → .env.prod

启动方式：
  python main.py                    # dev
  APP_ENV=test python main.py       # test
  APP_ENV=prod python main.py       # prod
  PowerShell: $env:APP_ENV="test"; python main.py
"""
import os
from pydantic_settings import BaseSettings

# 通过环境变量决定读取哪个 .env 文件
_APP_ENV = os.getenv("APP_ENV", "dev")
_ENV_FILE_MAP = {
    "dev":  ".env",
    "test": ".env.test",
    "prod": ".env.prod",
}
_env_file = _ENV_FILE_MAP.get(_APP_ENV, ".env")


class Settings(BaseSettings):
    # ===== 环境标识 =====
    APP_ENV: str = "dev"              # dev | test | prod
    APP_NAME: str = "小时光租衣舍"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ===== 数据库配置 =====
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str                  # 无默认值，强制从 .env 读取
    DB_NAME: str = "celestial_dev"

    # ===== JWT配置 =====
    JWT_SECRET_KEY: str               # 无默认值，强制从 .env 读取
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    # ===== 微信小程序配置 =====
    WECHAT_APP_ID: str = "your-wechat-app-id"
    WECHAT_APP_SECRET: str = "your-wechat-app-secret"

    # ===== 微信支付配置 =====
    WECHAT_PAY_MCH_ID: str = ""
    WECHAT_PAY_PRIVATE_KEY: str = ""
    WECHAT_PAY_SERIAL_NO: str = ""
    WECHAT_PAY_APIV3_KEY: str = ""

    # ===== TTLock配置（预留）=====
    TTLOCK_CLIENT_ID: str = ""
    TTLOCK_CLIENT_SECRET: str = ""
    TTLOCK_ACCESS_TOKEN: str = ""

    # ===== CORS配置 =====
    # dev/test: ["*"]  prod: ["https://servicewechat.com"]
    CORS_ORIGINS: list = ["*"]

    # ===== AI配置 =====
    GEMINI_API_KEY: str = ""
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    AI_SERVICE_TYPE: str = "deepseek"  # deepseek | gemini

    class Config:
        env_file = _env_file           # 动态加载对应环境配置文件
        case_sensitive = True


settings = Settings()

# ===== 衍生环境判断（在模块中使用方便）=====
IS_DEV  = settings.APP_ENV == "dev"
IS_TEST = settings.APP_ENV == "test"
IS_PROD = settings.APP_ENV == "prod"

# ===== 数据库连接URL =====
DATABASE_URL = (
    f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8mb4"
)
