import os

# Set environment before any imports
os.environ["DATABASE_URL"] = "sqlite:///test.db"
os.environ["JWT_SECRET"] = "test_secret"
os.environ["TESTING"] = "true"

from fastapi.testclient import TestClient
from main import app
from models.base import Base
from models.user import UserTable
from models.project import ProjectTable
from services.database_service import get_db_service
from middleware.auth_middleware import verify_token

# Create tables manually
print("Setting up database...")
db_service = get_db_service()
print(f"Database URL: {db_service.engine.url}")
print(f"Engine ID: {id(db_service.engine)}")
Base.metadata.create_all(bind=db_service.engine)
print("Tables created")

# Check if the same engine is used in project service
from services.project_service import get_project_service
project_service = get_project_service()
print(f"Project service engine ID: {id(project_service.db_service.engine)}")
print(f"Project service DB URL: {project_service.db_service.engine.url}")

# Mock auth
def mock_verify_token():
    return "00000000-0000-0000-0000-000000000001"

app.dependency_overrides[verify_token] = mock_verify_token

# Test
client = TestClient(app)
response = client.get("/projects?page=1&limit=10")
print(f"Status: {response.status_code}")
if response.status_code != 200:
    print(f"Error: {response.text}")
else:
    print(f"Success: {response.json()}") 

# Test file 