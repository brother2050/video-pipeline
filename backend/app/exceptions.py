"""
自定义异常类 + FastAPI 异常处理器。
所有异常都返回统一 APIResponse 格式。
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


# --- 业务异常 ---

class AppError(Exception):
    """应用层错误基类"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    """资源不存在"""
    def __init__(self, resource: str, resource_id: str):
        super().__init__(f"{resource} not found: {resource_id}", status_code=404)


class ConflictError(AppError):
    """状态冲突"""
    def __init__(self, message: str):
        super().__init__(message, status_code=409)


class ValidationError(AppError):
    """业务校验失败"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class PipelineError(AppError):
    """流水线错误"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


class GenerationError(AppError):
    """AI 生成错误"""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class SupplierError(AppError):
    """供应商错误基类"""
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message, status_code=status_code)


class SupplierConnectionError(SupplierError):
    def __init__(self, provider: str, detail: str = ""):
        super().__init__(f"Connection to {provider} failed: {detail}", status_code=502)


class SupplierTimeoutError(SupplierError):
    def __init__(self, provider: str, timeout: int):
        super().__init__(f"{provider} timed out after {timeout}s", status_code=504)


class SupplierAPIError(SupplierError):
    def __init__(self, provider: str, status_code: int, detail: str):
        super().__init__(f"{provider} API error {status_code}: {detail}", status_code=502)


class AllSuppliersExhausted(SupplierError):
    def __init__(self, capability: str, errors: list[str]):
        error_summary = "; ".join(errors)
        super().__init__(
            f"All suppliers for {capability} exhausted. Errors: {error_summary}",
            status_code=503,
        )


class UnsupportedOperationError(AppError):
    def __init__(self, message: str):
        super().__init__(message, status_code=400)


# --- 异常处理器注册 ---

def register_exception_handlers(app: FastAPI) -> None:
    """注册所有异常处理器到 FastAPI app"""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "data": None,
                "message": exc.message,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "message": "Internal server error",
            },
        )
