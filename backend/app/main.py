from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import planner, intent, flights, destination, attractions, hotels, daily_schedule, transport, dining, cost, itinerary, state
from app.core.exceptions import BaseAppError
from app.core.logging import setup_logging
from app.config import settings

# 初始化日志
setup_logging()

app = FastAPI(title="Travel Agent API")

# 设置 CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 注册全局异常处理器
@app.exception_handler(BaseAppError)
async def app_exception_handler(request: Request, exc: BaseAppError):
    return JSONResponse(
        status_code=exc.code if 100 <= exc.code <= 599 else 400,
        content={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details
        },
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "details": None
        },
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": "参数验证失败",
            "details": exc.errors()
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # 对于未捕获的常规异常，记录日志并返回500
    # 这里为了简便直接返回，实际生产环境应记录详细堆栈
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": f"服务器内部错误: {str(exc)}",
            "details": None
        },
    )

app.include_router(planner.router)
app.include_router(intent.router)
app.include_router(flights.router)
app.include_router(destination.router)
app.include_router(attractions.router)
app.include_router(hotels.router, prefix="/api/v1/hotels", tags=["Hotels"])
app.include_router(daily_schedule.router, prefix="/api/v1/schedules", tags=["Daily Schedule"])
app.include_router(transport.router, prefix="/api/v1/transport", tags=["Transport"])
app.include_router(dining.router)
app.include_router(cost.router)
app.include_router(itinerary.router, prefix="/api/v1/itinerary", tags=["Itinerary Output"])
app.include_router(state.router, prefix="/api/v1/state", tags=["Planning State Machine"])
@app.get("/")
async def root():
    return {"message": "Travel Agent API is running"}
