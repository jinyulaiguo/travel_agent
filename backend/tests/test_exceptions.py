import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import app
from app.core.exceptions import BusinessError, NotFoundError

client = TestClient(app)

def test_business_error_handler():
    # 模拟一个触发 BusinessError 的路由
    @app.get("/test-business-error")
    async def trigger_business_error():
        raise BusinessError("业务异常测试", code=4002, details={"item": "test"})

    response = client.get("/test-business-error")
    assert response.status_code == 400
    assert response.json() == {
        "code": 4002,
        "message": "业务异常测试",
        "details": {"item": "test"}
    }

def test_not_found_error_handler():
    @app.get("/test-not-found-error")
    async def trigger_not_found_error():
        raise NotFoundError("User", 123)

    response = client.get("/test-not-found-error")
    assert response.status_code == 404
    assert response.json() == {
        "code": 404,
        "message": "未找到资源 User: 123",
        "details": None
    }

def test_validation_error_handler():
    @app.get("/test-validation-error/{id}")
    async def trigger_validation_error(id: int):
        return {"id": id}

    # 传入非整数触发校验错误
    response = client.get("/test-validation-error/abc")
    assert response.status_code == 422
    data = response.json()
    assert data["code"] == 422
    assert data["message"] == "参数验证失败"
    assert "details" in data

def test_404_handler():
    response = client.get("/non-existent-route")
    assert response.status_code == 404
    assert response.json() == {
        "code": 404,
        "message": "Not Found",
        "details": None
    }
