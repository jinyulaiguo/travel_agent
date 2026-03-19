import logging
import os
from importlib import reload
import app.config
import app.core.logging

def test_logging_level_from_settings():
    # 测试默认级别
    from app.config import settings
    from app.core.logging import setup_logging
    
    setup_logging()
    root_logger = logging.getLogger()
    # 默认是 INFO
    assert root_logger.level == logging.INFO

def test_logging_level_from_env(monkeypatch):
    # 模拟环境变量更改
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    
    # 重新加载配置以反映环境变量更改
    # 必须重新加载由于 settings 是在模块加载时实例化的
    import app.config
    reload(app.config)
    
    import app.core.logging
    reload(app.core.logging)
    
    from app.core.logging import setup_logging
    setup_logging()
    
    root_logger = logging.getLogger()
    assert root_logger.level == logging.DEBUG
