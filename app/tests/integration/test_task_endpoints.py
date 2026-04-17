import pytest
from httpx import AsyncClient


async def _register_and_login(client: AsyncClient, email: str, password: str = "password123") -> str:
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    res = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return res.json()["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
class TestTaskEndpoints:
    async def test_create_task(self, client: AsyncClient):
        token = await _register_and_login(client, "create@task.com")
        res = await client.post("/api/v1/tasks", json={
            "title": "My First Task", "status": "pending", "priority": "medium"
        }, headers=auth_headers(token))
        assert res.status_code == 201
        data = res.json()
        assert data["title"] == "My First Task"
        assert data["status"] == "pending"

    async def test_list_tasks_returns_paginated(self, client: AsyncClient):
        token = await _register_and_login(client, "list@task.com")
        hdrs  = auth_headers(token)
        for i in range(3):
            await client.post("/api/v1/tasks", json={
                "title": f"Task {i}", "status": "pending", "priority": "low"
            }, headers=hdrs)

        res = await client.get("/api/v1/tasks?limit=2&offset=0", headers=hdrs)
        assert res.status_code == 200
        data = res.json()
        assert data["total"] == 3
        assert len(data["items"]) == 2

    async def test_get_task_by_id(self, client: AsyncClient):
        token = await _register_and_login(client, "get@task.com")
        hdrs  = auth_headers(token)
        created = await client.post("/api/v1/tasks", json={
            "title": "Specific Task", "status": "pending", "priority": "high"
        }, headers=hdrs)
        task_id = created.json()["id"]

        res = await client.get(f"/api/v1/tasks/{task_id}", headers=hdrs)
        assert res.status_code == 200
        assert res.json()["id"] == task_id

    async def test_update_task(self, client: AsyncClient):
        token = await _register_and_login(client, "update@task.com")
        hdrs  = auth_headers(token)
        created = await client.post("/api/v1/tasks", json={
            "title": "Old Title", "status": "pending", "priority": "medium"
        }, headers=hdrs)
        task_id = created.json()["id"]

        res = await client.put(f"/api/v1/tasks/{task_id}", json={
            "title": "New Title", "status": "done"
        }, headers=hdrs)
        assert res.status_code == 200
        assert res.json()["title"] == "New Title"
        assert res.json()["status"] == "done"

    async def test_delete_task(self, client: AsyncClient):
        token = await _register_and_login(client, "delete@task.com")
        hdrs  = auth_headers(token)
        created = await client.post("/api/v1/tasks", json={
            "title": "To Be Deleted", "status": "pending", "priority": "low"
        }, headers=hdrs)
        task_id = created.json()["id"]

        del_res = await client.delete(f"/api/v1/tasks/{task_id}", headers=hdrs)
        assert del_res.status_code == 204

        get_res = await client.get(f"/api/v1/tasks/{task_id}", headers=hdrs)
        assert get_res.status_code == 404

    async def test_filter_by_status(self, client: AsyncClient):
        token = await _register_and_login(client, "filter@task.com")
        hdrs  = auth_headers(token)
        await client.post("/api/v1/tasks", json={"title": "Done Task", "status": "done", "priority": "low"}, headers=hdrs)
        await client.post("/api/v1/tasks", json={"title": "Pending Task", "status": "pending", "priority": "low"}, headers=hdrs)

        res = await client.get("/api/v1/tasks?status=done", headers=hdrs)
        assert res.status_code == 200
        data = res.json()
        assert all(t["status"] == "done" for t in data["items"])

    async def test_unauthenticated_request_returns_403(self, client: AsyncClient):
        res = await client.get("/api/v1/tasks")
        assert res.status_code in (401, 403)
