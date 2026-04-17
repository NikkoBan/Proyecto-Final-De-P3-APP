import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthEndpoints:
    async def test_register_succeeds(self, client: AsyncClient):
        res = await client.post("/api/v1/auth/register", json={
            "email": "alpha@test.com",
            "password": "password123",
        })
        assert res.status_code == 201
        data = res.json()
        assert data["email"] == "alpha@test.com"
        assert "id" in data

    async def test_register_duplicate_email_returns_409(self, client: AsyncClient):
        payload = {"email": "dup@test.com", "password": "password123"}
        await client.post("/api/v1/auth/register", json=payload)
        res = await client.post("/api/v1/auth/register", json=payload)
        assert res.status_code == 409

    async def test_login_returns_tokens(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json={
            "email": "login@test.com", "password": "password123"
        })
        res = await client.post("/api/v1/auth/login", json={
            "email": "login@test.com", "password": "password123"
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert "refresh_token" in data

    async def test_login_wrong_password_returns_401(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json={
            "email": "wrong@test.com", "password": "password123"
        })
        res = await client.post("/api/v1/auth/login", json={
            "email": "wrong@test.com", "password": "wrongpass"
        })
        assert res.status_code == 401

    async def test_refresh_returns_new_tokens(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json={
            "email": "refresh@test.com", "password": "password123"
        })
        login = await client.post("/api/v1/auth/login", json={
            "email": "refresh@test.com", "password": "password123"
        })
        refresh_token = login.json()["refresh_token"]

        res = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert res.status_code == 200
        assert "access_token" in res.json()

    async def test_refresh_with_invalid_token_returns_401(self, client: AsyncClient):
        res = await client.post("/api/v1/auth/refresh", json={"refresh_token": "totally.invalid.token"})
        assert res.status_code == 401
