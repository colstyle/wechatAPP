# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback
import logging

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):
    """
    注册全局异常处理器，统一所有接口返回格式为 {code, message, data}
    """

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"====== Global Exception ======\nRequest: {request.method} {request.url}\nException: {traceback.format_exc()}")
        return JSONResponse(
            status_code=200, # 统一返回200前端好处理，或者保持500，按需修改
            content={"code": 500, "message": "服务器内部错误，请稍后再试", "data": None}
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        # 兼容自定义的异常抛出 (如 400 业务错误，401 鉴权失败)
        # 将 HTTP status 转换到业务 code 并返回200/或保留原状态码
        # 这里为了小程序兼容性最好统一 200 返回值，如果之前有约定用真实响应码，就用真实响应码。暂时不改变原有状态码逻辑，仅格式化body。
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": exc.status_code, "message": str(exc.detail), "data": None}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={"code": 422, "message": "参数校验错误", "data": exc.errors()}
        )
