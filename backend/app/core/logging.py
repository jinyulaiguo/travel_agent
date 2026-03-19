import logging
import sys
from app.config import settings


def setup_logging():
    """配置全局日志"""
    # 获取根日志记录器
    logging.basicConfig(
        level=settings.LOG_LEVEL.upper(),
        format=settings.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ],
        force=True
    )

    # 如果需要，可以针对特定模块调整日志级别
    # logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized with level: {settings.LOG_LEVEL}")
