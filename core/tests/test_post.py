import pytest
from httpx import AsyncClient


class TestPost:
    
    async def create_user_and_login(self, client: AsyncClient, username: str, email: str, password: str):
        user_data_reg = {
            "username": username,
            "email": email,
            "password": password
        }
        await client.post("/auth/register", json=user_data_reg)
        user_data_log = {
            "username": username,
            "password": password
        }
        response = await client.post("/auth/login", data=user_data_log, headers={"Content-Type": "application/x-www-form-urlencoded"})
        return response.json()["access_token"]

    @pytest.mark.asyncio
    async def test_post_create(self, client: AsyncClient):
        
        token = await self.create_user_and_login(client, "test", "test@example.com", "testPass")
        
        post_data = {
            "title": "first post",
            "description": "nothing"
        }

        response = await client.post("/posts/create", json=post_data, headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == post_data["title"]
        assert data["description"] in post_data["description"]
        assert "created_at" in data
        assert "author_id" in data
        assert "id" in data

    @pytest.mark.asyncio
    async def test_post_try_to_create_unauth(self, client: AsyncClient):
        post_data = {
            "title": "first post",
            "description": "nothing"
        }

        response = await client.post("/posts/create", json=post_data)

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_post_update_own_post(self, client: AsyncClient):
        token = await self.create_user_and_login(client, "test", "test@example.com", "testPass")
        post_data_create = {
            "title": "first post",
            "description": "nothing"
        }
        create_response = await client.post("/posts/create", json=post_data_create, headers={"Authorization": f"Bearer {token}"})
        post_data_update = {
            "title": "updated post",
            "description": "Something"
        }
        post_id = create_response.json()["id"]
        update_response = await client.patch(f"/posts/update/{post_id}", json=post_data_update, headers={"Authorization": f"Bearer {token}"})

        assert update_response.status_code == 200
        data = update_response.json()
        assert data["title"] == "updated post"
        assert data["description"] == "Something"

    @pytest.mark.asyncio
    async def test_post_get_all(self, client: AsyncClient):
        token = await self.create_user_and_login(client, "test", "test@example.com", "testPass")
        post_data1 = {
            "title": "post-1",
            "description": "nothing"
        } 
        post_data2 = {
            "title": "post-2",
            "description": "nothing"
        } 
        post_data3 = {
            "title": "post-3",
            "description": "nothing"
        }   
        await client.post("/posts/create", json=post_data1, headers={"Authorization": f"Bearer {token}"})
        await client.post("/posts/create", json=post_data2, headers={"Authorization": f"Bearer {token}"})
        await client.post("/posts/create", json=post_data3, headers={"Authorization": f"Bearer {token}"})

        response = await client.get("/posts/cursor")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_post_update_not_own_post(self, client: AsyncClient):
        token1 = await self.create_user_and_login(client, "test1", "test1@example.com", "testPass")
        post_data1 = {
            "title": "this post created by user with id: 1",
            "description": "nothing"
        }
        create_response = await client.post("/posts/create", json=post_data1, headers={"Authorization": f"Bearer {token1}"})
        post_id = create_response.json()["id"]
        await client.get("/auth/logout", headers={"Authorization": f"Bearer {token1}"})
        token2 = await self.create_user_and_login(client, "test2", "test2@example.com", "testPass")
        update_post_data1 = {
            "title": "updated_info",
            "description": "updated_info"
        }
        update_response = await client.patch(f"/posts/update/{post_id}", json=update_post_data1, headers={"Authorization": f"Bearer {token2}"})
        
        assert update_response.status_code == 403