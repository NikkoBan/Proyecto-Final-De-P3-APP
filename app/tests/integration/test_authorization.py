import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient, email: str) -> str:
    await client.post("/api/v1/auth/register", json={"email": email, "password": "password123"})
    res = await client.post("/api/v1/auth/login", json={"email": email, "password": "password123"})
    return res.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
class TestAuthorization:
    async def test_user_cannot_read_another_users_task(self, client: AsyncClient):
        token_a = await _register_and_login(client, "userA@auth.com")
        token_b = await _register_and_login(client, "userB@auth.com")

        created = await client.post("/api/v1/tasks", json={
            "title": "User A's Task", "status": "pending", "priority": "low"
        }, headers=auth_headers(token_a))
        task_id = created.json()["id"]

        res = await client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers(token_b))
        assert res.status_code == 404

    async def test_user_cannot_delete_another_users_task(self, client: AsyncClient):
        token_a = await _register_and_login(client, "ownerA@auth.com")
        token_b = await _register_and_login(client, "attackerB@auth.com")

        created = await client.post("/api/v1/tasks", json={
            "title": "Owner A Task", "status": "pending", "priority": "low"
        }, headers=auth_headers(token_a))
        task_id = created.json()["id"]

        res = await client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers(token_b))
        assert res.status_code == 404

    async def test_user_cannot_update_another_users_task(self, client: AsyncClient):
        token_a = await _register_and_login(client, "ownerAA@auth.com")
        token_b = await _register_and_login(client, "attackerBB@auth.com")

        created = await client.post("/api/v1/tasks", json={
            "title": "Protected Task", "status": "pending", "priority": "low"
        }, headers=auth_headers(token_a))
        task_id = created.json()["id"]

        res = await client.put(f"/api/v1/tasks/{task_id}", json={"title": "Hijacked"},
                               headers=auth_headers(token_b))
        assert res.status_code == 404

    async def test_tasks_list_only_shows_own_tasks(self, client: AsyncClient):
        token_a = await _register_and_login(client, "listA@auth.com")
        token_b = await _register_and_login(client, "listB@auth.com")

        await client.post("/api/v1/tasks", json={
            "title": "Only A can see this", "status": "pending", "priority": "low"
        }, headers=auth_headers(token_a))

        res = await client.get("/api/v1/tasks", headers=auth_headers(token_b))
        data = res.json()
        assert all("Only A" not in t["title"] for t in data["items"])
