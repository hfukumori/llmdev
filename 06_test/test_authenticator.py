import pytest
from authenticator import Authenticator

@pytest.fixture
def authenticator():
    auth = Authenticator()
    yield auth
    auth.users.clear()

def test_register_new_user(authenticator):
    authenticator.register("user1", "password1")
    assert "user1" in authenticator.users
    assert authenticator.users["user1"] == "password1"

def test_register_existing_user(authenticator):
    authenticator.register("user1", "password1")
    with pytest.raises(ValueError, match="エラー: ユーザーは既に存在します。"):
        authenticator.register("user1", "password2")

def test_login_success(authenticator):
    authenticator.register("user1", "password1")
    result = authenticator.login("user1", "password1")
    assert result == "ログイン成功"

def test_login_failure(authenticator):
    authenticator.register("user1", "password1")
    with pytest.raises(ValueError, match="エラー: ユーザー名またはパスワードが正しくありません。"):
        authenticator.login("user1", "wrongpassword")
