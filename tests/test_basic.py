def test_app_is_created(app):
    """测试 Flask 应用实例是否能正常创建"""
    assert app.name == 'app'

def test_home_page(client):
    """测试首页路由，确保应用能响应请求"""
    response = client.get("/")
    # 首页可能是 200 正常返回，也可能是 302 重定向到登录页
    assert response.status_code in [200, 302]
