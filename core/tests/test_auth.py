import pytest
from httpx import AsyncClient


class TestAuth:
    """Тесты авторизации и регистрации"""

    @pytest.mark.asyncio
    async def test_register(self, client: AsyncClient):
        user_data = {
            "username": "test",
            "email": "test@example.com",
            "password": "test_password"
        }

        response = await client.post("/auth/register", json=user_data)
    
        assert response.status_code == 200
        
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert "password" not in data
    
        assert "created_at" in data

    @pytest.mark.asyncio
    async def test_register_check_username_duplicate(self, client: AsyncClient):
        user_data1 = {
            "username": "test",
            "email": "test@example.com",
            "password": "test_password"
        }
        await client.post("/auth/register", json=user_data1)
        user_data2 = {
            "username": "test",
            "email": "test@example.com",
            "password": "test_password"
        }
        response = await client.post("/auth/register", json=user_data2)

        assert response.status_code == 400
        assert "пользователь с таким именем уже существует" in response.text.lower()

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient):
        user_data_reg = {
            "username": "test",
            "email": "test@example.com",
            "password": "test_password"
        }
        await client.post("/auth/register", json=user_data_reg)
        user_data_log = {
            "username": "test",
            "password": "test_password"
        }
        response = await client.post("/auth/login", data=user_data_log, headers={"Content-Type": "application/x-www-form-urlencoded"})

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 20

    @pytest.mark.asyncio
    async def test_login_check_wrond_password(self, client: AsyncClient):
        user_data_reg = {
            "username": "test",
            "email": "test@example.com",
            "password": "test_password"
        }
        await client.post("/auth/register", json=user_data_reg)
        user_data_log = {
            "username": "test",
            "password": "wrongpass"
        }
        response = await client.post("/auth/login", data=user_data_log, headers={"Context-Type": "application/x-www-form-urlencoded"})

        assert response.status_code == 401
        assert "Неверное имя пользователя или пароль" in response.text

    @pytest.mark.asyncio
    async def test_add_token_to_blacklist(self, client: AsyncClient):
        user_data_reg = {
            "username": "test",
            "email": "test@example.com",
            "password": "test_password"
        }
        await client.post("/auth/register", json=user_data_reg)
        user_data_log = {
            "username": "test",
            "password": "test_password"
        }
        login_response = await client.post("/auth/login", data=user_data_log, headers={"Content-Type": "application/x-www-form-urlencoded"})
        token = login_response.json()["access_token"]
        
        me_response = await client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        assert me_response.status_code == 200

        logout_response = await client.get("/auth/logout", headers={"Authorization": f"Bearer {token}"})
        assert logout_response.status_code == 200

        me_response_again = await client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
        assert me_response_again.status_code == 401
        assert "отозван" in me_response_again.text.lower()
    