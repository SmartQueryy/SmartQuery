from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List
import uuid

from models.response_schemas import (
    ApiResponse,
    Project,
    CreateProjectRequest,
    CreateProjectResponse,
    PaginatedResponse,
    PaginationParams,
    UploadStatusResponse,
    ColumnMetadata,
    ProjectStatus,
)
from api.auth import verify_token

router = APIRouter(prefix="/projects", tags=["projects"])

# Mock projects database
MOCK_PROJECTS = {
    "project_001": {
        "id": "project_001",
        "user_id": "user_001",
        "name": "Sales Data Analysis",
        "description": "Monthly sales data from Q4 2024",
        "csv_filename": "sales_data.csv",
        "csv_path": "user_001/project_001/sales_data.csv",
        "row_count": 1000,
        "column_count": 8,
        "columns_metadata": [
            {
                "name": "date",
                "type": "date",
                "nullable": False,
                "sample_values": ["2024-01-01", "2024-01-02", "2024-01-03"],
                "unique_count": 365,
            },
            {
                "name": "product_name",
                "type": "string",
                "nullable": False,
                "sample_values": ["Product A", "Product B", "Product C"],
                "unique_count": 50,
            },
            {
                "name": "sales_amount",
                "type": "number",
                "nullable": False,
                "sample_values": [1500.00, 2300.50, 1890.25],
                "unique_count": 950,
            },
            {
                "name": "quantity",
                "type": "number",
                "nullable": False,
                "sample_values": [10, 15, 12],
                "unique_count": 100,
            },
        ],
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T10:30:00Z",
        "status": "ready",
    },
    "project_002": {
        "id": "project_002",
        "user_id": "user_001",
        "name": "Customer Demographics",
        "description": "Customer data analysis",
        "csv_filename": "customers.csv",
        "csv_path": "user_001/project_002/customers.csv",
        "row_count": 500,
        "column_count": 6,
        "columns_metadata": [
            {
                "name": "customer_id",
                "type": "number",
                "nullable": False,
                "sample_values": [1, 2, 3],
                "unique_count": 500,
            },
            {
                "name": "age",
                "type": "number",
                "nullable": True,
                "sample_values": [25, 30, 45],
                "unique_count": 60,
            },
            {
                "name": "city",
                "type": "string",
                "nullable": False,
                "sample_values": ["New York", "Los Angeles", "Chicago"],
                "unique_count": 25,
            },
        ],
        "created_at": "2025-01-02T00:00:00Z",
        "updated_at": "2025-01-02T08:15:00Z",
        "status": "ready",
    },
}


@router.get("")
async def get_projects(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_id: str = Depends(verify_token),
) -> ApiResponse[PaginatedResponse[Project]]:
    """Get user's projects with pagination"""

    # Filter projects by user_id
    user_projects = [
        Project(**project_data)
        for project_data in MOCK_PROJECTS.values()
        if project_data["user_id"] == user_id
    ]

    # Apply pagination
    total = len(user_projects)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    projects_page = user_projects[start_idx:end_idx]

    paginated_response = PaginatedResponse(
        items=projects_page,
        total=total,
        page=page,
        limit=limit,
        hasMore=end_idx < total,
    )

    return ApiResponse(success=True, data=paginated_response)


@router.post("")
async def create_project(
    request: CreateProjectRequest, user_id: str = Depends(verify_token)
) -> ApiResponse[CreateProjectResponse]:
    """Create new project"""

    project_id = str(uuid.uuid4())

    project = Project(
        id=project_id,
        user_id=user_id,
        name=request.name,
        description=request.description,
        csv_filename="",  # Will be set after upload
        csv_path=f"{user_id}/{project_id}/",
        row_count=0,
        column_count=0,
        columns_metadata=[],
        created_at=datetime.utcnow().isoformat() + "Z",
        updated_at=datetime.utcnow().isoformat() + "Z",
        status=ProjectStatus.UPLOADING,
    )

    # Mock upload URL and fields
    upload_url = f"https://mock-storage.example.com/upload"
    upload_fields = {
        "key": f"{user_id}/{project_id}/data.csv",
        "policy": "mock_base64_policy",
        "signature": "mock_signature",
        "x-amz-algorithm": "AWS4-HMAC-SHA256",
        "x-amz-credential": "mock_credentials",
    }

    # Store in mock database
    MOCK_PROJECTS[project_id] = project.model_dump()

    response = CreateProjectResponse(
        project=project, upload_url=upload_url, upload_fields=upload_fields
    )

    return ApiResponse(success=True, data=response)


@router.get("/{project_id}")
async def get_project(
    project_id: str, user_id: str = Depends(verify_token)
) -> ApiResponse[Project]:
    """Get project details"""

    if project_id not in MOCK_PROJECTS:
        raise HTTPException(status_code=404, detail="Project not found")

    project_data = MOCK_PROJECTS[project_id]

    # Check ownership
    if project_data["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    project = Project(**project_data)
    return ApiResponse(success=True, data=project)


@router.delete("/{project_id}")
async def delete_project(
    project_id: str, user_id: str = Depends(verify_token)
) -> ApiResponse[Dict[str, str]]:
    """Delete project"""

    if project_id not in MOCK_PROJECTS:
        raise HTTPException(status_code=404, detail="Project not found")

    project_data = MOCK_PROJECTS[project_id]

    # Check ownership
    if project_data["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Delete from mock database
    del MOCK_PROJECTS[project_id]

    return ApiResponse(success=True, data={"message": "Project deleted successfully"})


@router.get("/{project_id}/upload-url")
async def get_upload_url(
    project_id: str, user_id: str = Depends(verify_token)
) -> ApiResponse[Dict[str, Any]]:
    """Get presigned URL for file upload"""

    if project_id not in MOCK_PROJECTS:
        raise HTTPException(status_code=404, detail="Project not found")

    project_data = MOCK_PROJECTS[project_id]

    # Check ownership
    if project_data["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    upload_data = {
        "upload_url": f"https://mock-storage.example.com/upload",
        "upload_fields": {
            "key": f"{user_id}/{project_id}/data.csv",
            "policy": "mock_base64_policy",
            "signature": "mock_signature",
        },
    }

    return ApiResponse(success=True, data=upload_data)


@router.get("/{project_id}/status")
async def get_project_status(
    project_id: str, user_id: str = Depends(verify_token)
) -> ApiResponse[UploadStatusResponse]:
    """Get project processing status"""

    if project_id not in MOCK_PROJECTS:
        raise HTTPException(status_code=404, detail="Project not found")

    project_data = MOCK_PROJECTS[project_id]

    # Check ownership
    if project_data["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Mock status based on project status
    status_response = UploadStatusResponse(
        project_id=project_id,
        status=project_data["status"],
        progress=100 if project_data["status"] == "ready" else 75,
        message=(
            "Processing complete"
            if project_data["status"] == "ready"
            else "Analyzing CSV schema..."
        ),
    )

    return ApiResponse(success=True, data=status_response)
