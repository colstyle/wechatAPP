# -*- coding: utf-8 -*-
"""
小时光租衣舍 - 主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入路由
from app.api import user, product, order, subscription, appointment, review, ai, admin


# 注册路由
app.include_router(user.router, prefix="/api/user", tags=["用户"])
app.include_router(product.router, prefix="/api/product", tags=["商品"])
app.include_router(order.router, prefix="/api/order", tags=["订单"])
app.include_router(subscription.router, prefix="/api/subscription", tags=["订阅"])
app.include_router(appointment.router, prefix="/api/appointment", tags=["预约"])
app.include_router(review.router, prefix="/api/review", tags=["评价"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI智能客服"])
app.include_router(admin.router, prefix="/api/admin", tags=["店主后台"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
