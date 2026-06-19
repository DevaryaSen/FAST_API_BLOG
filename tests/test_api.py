"""Basic API tests."""
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from config import settings
from database import Base, get_db
from main import app

TEST_DATABASE_URL = settings.database_url

test_engine = create_async_engine(TEST_DATABASE_URL)
TestSessionLocal = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture
async def auth_client(client):
    """Client with a registered + logged-in user."""
    await client.post("/api/users", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
    })
    res = await client.post("/api/users/token", data={
        "username": "test@example.com",
        "password": "testpass123",
    })
    token = res.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


async def test_health(client):
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


async def test_register(client):
    res = await client.post("/api/users", json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "password123",
    })
    assert res.status_code == 201
    assert res.json()["username"] == "alice"


async def test_login(client):
    await client.post("/api/users", json={
        "username": "bob",
        "email": "bob@example.com",
        "password": "password123",
    })
    res = await client.post("/api/users/token", data={
        "username": "bob@example.com",
        "password": "password123",
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


async def test_create_post(auth_client):
    res = await auth_client.post("/api/posts", json={
        "title": "Hello World",
        "content": "This is my first post.",
    })
    assert res.status_code == 201
    assert res.json()["title"] == "Hello World"


async def test_get_posts(auth_client):
    await auth_client.post("/api/posts", json={"title": "Post 1", "content": "Content 1"})
    res = await auth_client.get("/api/posts")
    assert res.status_code == 200
    assert res.json()["total"] == 1


async def test_delete_post(auth_client):
    create_res = await auth_client.post("/api/posts", json={"title": "Temp", "content": "Content"})
    post_id = create_res.json()["id"]
    res = await auth_client.delete(f"/api/posts/{post_id}")
    assert res.status_code == 204


async def test_duplicate_email(client):
    await client.post("/api/users", json={"username": "u1", "email": "dup@example.com", "password": "pass1234"})
    res = await client.post("/api/users", json={"username": "u2", "email": "dup@example.com", "password": "pass1234"})
    assert res.status_code == 400
