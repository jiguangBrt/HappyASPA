import pytest
import sys
import os

# 将项目根目录添加到 Python 路径，以便能够导入 app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

@pytest.fixture
def app():
    """创建一个用于测试的 Flask 应用实例"""
    app = create_app()
    app.config.update({
        "TESTING": True,
        # 使用内存数据库，避免污染开发/生产数据库
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
    })
    yield app

@pytest.fixture
def client(app):
    """创建一个测试客户端，用于模拟发送 HTTP 请求"""
    return app.test_client()

def test_app_is_created(app):
    """测试 Flask 应用实例是否能正常创建"""
    assert app.name == 'app'

def test_home_page(client):
    """测试首页路由，确保应用能响应请求"""
    response = client.get("/")
    # 首页可能是 200 正常返回，也可能是 302 重定向到登录页
    assert response.status_code in [200, 302]
