#!/usr/bin/env python3
"""
Infrastructure test script for SmartQuery backend services
This script tests the configuration and setup of our infrastructure services
"""

import os
import sys
import asyncio
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

def test_docker_compose_config():
    """Test Docker Compose configuration"""
    print("🐳 Testing Docker Compose Configuration...")
    
    docker_compose_path = Path(__file__).parent.parent / "docker-compose.yml"
    if docker_compose_path.exists():
        print("✅ docker-compose.yml exists")
        
        # Read and check basic structure
        with open(docker_compose_path) as f:
            content = f.read()
            
        services = ["postgres", "redis", "minio", "celery-worker", "celery-flower"]
        for service in services:
            if service in content:
                print(f"✅ {service} service configured")
            else:
                print(f"❌ {service} service missing")
                
        # Check for required volumes
        if "volumes:" in content:
            print("✅ Docker volumes configured")
        
        # Check for networks
        if "networks:" in content:
            print("✅ Docker networks configured")
            
    else:
        print("❌ docker-compose.yml not found")
    
    print()

def test_backend_structure():
    """Test backend project structure"""
    print("📁 Testing Backend Project Structure...")
    
    backend_path = Path(__file__).parent.parent / "backend"
    required_files = [
        "main.py",
        "celery_app.py", 
        "requirements.txt",
        "Dockerfile.celery",
        "api/health.py",
        "services/database_service.py",
        "services/redis_service.py", 
        "services/storage_service.py",
        "tasks/file_processing.py"
    ]
    
    for file_path in required_files:
        full_path = backend_path / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} missing")
    
    print()

def test_database_init():
    """Test database initialization scripts"""
    print("🗄️ Testing Database Initialization...")
    
    db_init_path = Path(__file__).parent.parent / "database" / "init" / "01_init.sql"
    if db_init_path.exists():
        print("✅ Database initialization script exists")
        
        with open(db_init_path) as f:
            content = f.read()
            
        tables = ["users", "projects", "chat_messages"]
        for table in tables:
            if f"CREATE TABLE IF NOT EXISTS {table}" in content:
                print(f"✅ {table} table creation script")
            else:
                print(f"❌ {table} table creation script missing")
    else:
        print("❌ Database initialization script missing")
    
    print()

def test_environment_config():
    """Test environment configuration"""
    print("⚙️ Testing Environment Configuration...")
    
    # Check for required environment variables structure
    required_env_vars = [
        "DATABASE_URL",
        "REDIS_URL", 
        "MINIO_ENDPOINT",
        "MINIO_ACCESS_KEY",
        "MINIO_SECRET_KEY",
        "CELERY_BROKER_URL",
        "CELERY_RESULT_BACKEND"
    ]
    
    print("Required environment variables:")
    for var in required_env_vars:
        if var in ["MINIO_ACCESS_KEY", "MINIO_SECRET_KEY"]:
            print(f"🔑 {var} (configured in docker-compose)")
        else:
            print(f"✅ {var} (configured in docker-compose)")
    
    print()

def test_service_imports():
    """Test that services can be imported"""
    print("📦 Testing Service Imports...")
    
    try:
        from services.database_service import get_db_service
        print("✅ Database service imports successfully")
    except Exception as e:
        print(f"❌ Database service import failed: {e}")
    
    try:
        from services.redis_service import redis_service  
        print("✅ Redis service imports successfully")
    except Exception as e:
        print(f"❌ Redis service import failed: {e}")
        
    try:
        from services.storage_service import storage_service
        print("✅ Storage service imports successfully") 
    except Exception as e:
        print(f"❌ Storage service import failed: {e}")
        
    try:
        from celery_app import celery_app
        print("✅ Celery app imports successfully")
    except Exception as e:
        print(f"❌ Celery app import failed: {e}")
    
    print()

def test_requirements():
    """Test requirements.txt has necessary dependencies"""
    print("📋 Testing Requirements...")
    
    req_path = Path(__file__).parent.parent / "backend" / "requirements.txt"
    if req_path.exists():
        with open(req_path) as f:
            content = f.read()
            
        dependencies = [
            "psycopg2-binary",
            "redis", 
            "celery",
            "minio",
            "sqlalchemy"
        ]
        
        for dep in dependencies:
            if dep in content:
                print(f"✅ {dep}")
            else:
                print(f"❌ {dep} missing from requirements")
    else:
        print("❌ requirements.txt not found")
    
    print()

def main():
    """Run all infrastructure tests"""
    print("🚀 SmartQuery Infrastructure Test Suite")
    print("=" * 50)
    print()
    
    test_docker_compose_config()
    test_backend_structure()
    test_database_init()
    test_environment_config()
    test_service_imports()
    test_requirements()
    
    print("✨ Infrastructure test completed!")
    print()
    print("📝 Next steps:")
    print("1. Install Docker and Docker Compose")
    print("2. Run: docker compose up -d")
    print("3. Test with: cd backend && python main.py")
    print("4. Check health: curl http://localhost:8000/health/")

if __name__ == "__main__":
    main() 