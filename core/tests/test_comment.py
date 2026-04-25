import pytest
from httpx import AsyncClient




class TestComment:
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

    
    async def test_create_comment(self, client: AsyncClient):
        token = await self.create_user_and_login(client, "test", "test@example.com", "testPass")
        post_data = {
            "title": "post created",
            "description": "empty post"
        }
        response_post = await client.post("/posts/create", json=post_data, headers={"Authorization": f"Bearer {token}"})
        assert response_post.status_code == 201
        post_id = response_post.json()["id"]
        comment_data = {
            "content": "created comment"
        }
        response_comment = await client.post(f"/comments/{post_id}/comments", json=comment_data, headers={"Authorization": f"Bearer {token}"})
        assert response_comment.status_code == 200
        data = response_comment.json()
    
        assert data["content"] == comment_data["content"]
        assert "id" in data
        assert "author_id" in data
        assert "post_id" in data
        assert "content" in data
        assert "created_at" in data
        assert "is_edited" in data
        assert "edited_at" in data