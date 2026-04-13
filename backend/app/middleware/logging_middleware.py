# -*- coding: utf-8 -*-
"""
接口访问日志中间件
"""
import time
import logging
import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from config import settings

logger = logging.getLogger("api_access")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 记录请求前信息
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        url = request.url.path
        
        # 忽略健康检查和静态资源
        if url in ["/health", "/"] or url.startswith("/static"):
            return await call_next(request)
        
        # 执行请求
        response = await call_next(request)
        
        process_time = time.time() - start_time
        status_code = response.status_code
        
        # 打印简明的 API 访问日志
        logger.info(
            f"[{method}] {url} | Status: {status_code} | IP: {client_ip} | "
            f"Time: {process_time:.3f}s"
        )
        
        # 将处理时间放入响应头
        response.headers["X-Process-Time"] = str(process_time)
        return response

def setup_logging():
    """配置项目日志"""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    # 对于一些嘈杂的第三方库降低日志级别
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
