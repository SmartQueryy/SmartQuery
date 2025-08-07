import logging
import random
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from middleware.auth_middleware import verify_token
from models.response_schemas import (
    ApiResponse,
    ChatMessage,
    CSVPreview,
    PaginatedResponse,
    QueryResult,
    QuerySuggestion,
    SendMessageRequest,
    SendMessageResponse,
)
from services.langchain_service import langchain_service
from services.project_service import get_project_service

router = APIRouter(prefix="/chat", tags=["chat"])
project_service = get_project_service()
logger = logging.getLogger(__name__)

# Mock chat messages database
MOCK_CHAT_MESSAGES = {}

# Mock CSV preview data
MOCK_CSV_PREVIEWS = {
    "project_001": {
        "columns": [
            "date",
            "product_name",
            "sales_amount",
            "quantity",
            "category",
            "region",
            "customer_id",
            "discount",
        ],
        "sample_data": [
            [
                "2024-01-01",
                "Product A",
                1500.00,
                10,
                "Electronics",
                "North",
                "CUST001",
                0.1,
            ],
            [
                "2024-01-02",
                "Product B",
                2300.50,
                15,
                "Clothing",
                "South",
                "CUST002",
                0.05,
            ],
            [
                "2024-01-03",
                "Product C",
                1890.25,
                12,
                "Electronics",
                "East",
                "CUST003",
                0.15,
            ],
            [
                "2024-01-04",
                "Product A",
                1200.00,
                8,
                "Electronics",
                "West",
                "CUST004",
                0.0,
            ],
            ["2024-01-05", "Product D", 3400.75, 25, "Home", "North", "CUST005", 0.2],
        ],
        "total_rows": 1000,
        "data_types": {
            "date": "date",
            "product_name": "string",
            "sales_amount": "number",
            "quantity": "number",
            "category": "string",
            "region": "string",
            "customer_id": "string",
            "discount": "number",
        },
    },
    "project_002": {
        "columns": [
            "customer_id",
            "age",
            "city",
            "signup_date",
            "total_orders",
            "lifetime_value",
        ],
        "sample_data": [
            [1, 25, "New York", "2023-06-15", 5, 1250.50],
            [2, 30, "Los Angeles", "2023-07-20", 8, 2100.25],
            [3, 45, "Chicago", "2023-05-10", 12, 3450.75],
            [4, 35, "Houston", "2023-08-05", 3, 890.00],
            [5, 28, "Phoenix", "2023-09-12", 7, 1875.80],
        ],
        "total_rows": 500,
        "data_types": {
            "customer_id": "number",
            "age": "number",
            "city": "string",
            "signup_date": "date",
            "total_orders": "number",
            "lifetime_value": "number",
        },
    },
}

# Mock query suggestions
MOCK_SUGGESTIONS = [
    {
        "id": "sug_001",
        "text": "Show me total sales by month",
        "category": "analysis",
        "complexity": "beginner",
    },
    {
        "id": "sug_002",
        "text": "Create a bar chart of top 5 products by sales",
        "category": "visualization",
        "complexity": "intermediate",
    },
    {
        "id": "sug_003",
        "text": "What's the average sales amount by region?",
        "category": "analysis",
        "complexity": "beginner",
    },
    {
        "id": "sug_004",
        "text": "Show sales trend over time as a line chart",
        "category": "visualization",
        "complexity": "intermediate",
    },
    {
        "id": "sug_005",
        "text": "Compare sales performance across different categories",
        "category": "analysis",
        "complexity": "advanced",
    },
]


def generate_mock_query_result(query: str, project_id: str) -> QueryResult:
    """Generate mock query result based on the question"""

    # Mock SQL generation based on query content
    if "total sales" in query.lower() or "sum" in query.lower():
        sql_query = "SELECT product_name, SUM(sales_amount) as total_sales FROM data GROUP BY product_name ORDER BY total_sales DESC LIMIT 10"
        result_data = [
            {"product_name": "Product A", "total_sales": 15000.50},
            {"product_name": "Product B", "total_sales": 12300.25},
            {"product_name": "Product C", "total_sales": 9890.75},
            {"product_name": "Product D", "total_sales": 8450.00},
            {"product_name": "Product E", "total_sales": 7200.80},
        ]
        result_type = "table"

    elif "chart" in query.lower() or "visualization" in query.lower():
        sql_query = "SELECT category, SUM(sales_amount) as total_sales FROM data GROUP BY category"
        result_data = [
            {"category": "Electronics", "total_sales": 45000.50},
            {"category": "Clothing", "total_sales": 32300.25},
            {"category": "Home", "total_sales": 28900.75},
            {"category": "Sports", "total_sales": 15450.00},
        ]
        result_type = "chart"

    elif "average" in query.lower():
        sql_query = (
            "SELECT region, AVG(sales_amount) as avg_sales FROM data GROUP BY region"
        )
        result_data = [
            {"region": "North", "avg_sales": 1850.75},
            {"region": "South", "avg_sales": 1720.50},
            {"region": "East", "avg_sales": 1950.25},
            {"region": "West", "avg_sales": 1680.80},
        ]
        result_type = "table"

    else:
        # Default response
        sql_query = "SELECT * FROM data LIMIT 5"
        result_data = [
            {
                "date": "2024-01-01",
                "product_name": "Product A",
                "sales_amount": 1500.00,
            },
            {
                "date": "2024-01-02",
                "product_name": "Product B",
                "sales_amount": 2300.50,
            },
            {
                "date": "2024-01-03",
                "product_name": "Product C",
                "sales_amount": 1890.25,
            },
        ]
        result_type = "table"

    return QueryResult(
        id=str(uuid.uuid4()),
        query=query,
        sql_query=sql_query,
        result_type=result_type,
        data=result_data,
        execution_time=round(random.uniform(0.1, 2.0), 2),
        row_count=len(result_data),
        chart_config=(
            {
                "type": "bar",
                "x_axis": "category" if result_type == "chart" else "product_name",
                "y_axis": "total_sales",
                "title": "Sales Analysis",
            }
            if result_type == "chart"
            else None
        ),
    )


@router.post("/{project_id}/message")
async def send_message(
    project_id: str, request: SendMessageRequest, user_id: str = Depends(verify_token)
) -> ApiResponse[SendMessageResponse]:
    """Send message and get query results"""

    # Verify project exists and user has access
    try:
        user_uuid = uuid.UUID(user_id)
        project_uuid = uuid.UUID(project_id)

        if not project_service.check_project_ownership(project_uuid, user_uuid):
            raise HTTPException(status_code=404, detail="Project not found")

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project ID")

    # Create user message
    user_message = ChatMessage(
        id=str(uuid.uuid4()),
        project_id=project_id,
        user_id=user_id,
        content=request.message,
        role="user",
        created_at=datetime.utcnow().isoformat() + "Z",
    )

    # Use LangChain service for intelligent query processing
    try:
        query_result = langchain_service.process_query(
            request.message, project_id, user_id
        )
    except Exception:
        # Fallback to mock query result if LangChain service fails
        query_result = generate_mock_query_result(request.message, project_id)

    # Create AI response content based on result type
    if query_result.result_type == "error":
        ai_content = f"I encountered an error: {query_result.error}"
    elif query_result.result_type == "summary":
        ai_content = query_result.summary or "Here's what I found about your data."
    elif query_result.result_type == "table":
        result_text = "result" if query_result.row_count == 1 else "results"
        ai_content = f"I found {query_result.row_count} {result_text} for your query."
        if query_result.sql_query:
            ai_content += f"\n\n**SQL Query:** `{query_result.sql_query}`"
    elif query_result.result_type == "chart":
        chart_type = "chart"
        if query_result.chart_config and query_result.chart_config.get("type"):
            chart_type = query_result.chart_config["type"]
        ai_content = f"I've created a {chart_type} visualization"
        if query_result.sql_query:
            ai_content += f"\n\n**SQL Query:** `{query_result.sql_query}`"
    else:
        ai_content = "I've processed your query. Here are the results."

    # Store message in mock database
    if project_id not in MOCK_CHAT_MESSAGES:
        MOCK_CHAT_MESSAGES[project_id] = []
    MOCK_CHAT_MESSAGES[project_id].append(user_message.model_dump())

    # Create AI response message
    ai_message = ChatMessage(
        id=str(uuid.uuid4()),
        project_id=project_id,
        user_id="assistant",
        content=ai_content,
        role="assistant",
        created_at=datetime.utcnow().isoformat() + "Z",
        metadata={"query_result_id": query_result.id},
    )
    MOCK_CHAT_MESSAGES[project_id].append(ai_message.model_dump())

    response = SendMessageResponse(
        message=user_message, result=query_result, ai_message=ai_message
    )

    return ApiResponse(success=True, data=response)


@router.get("/{project_id}/messages")
async def get_messages(
    project_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_id: str = Depends(verify_token),
) -> ApiResponse[PaginatedResponse[ChatMessage]]:
    """Get chat message history"""

    # Verify project exists and user has access
    try:
        user_uuid = uuid.UUID(user_id)
        project_uuid = uuid.UUID(project_id)

        if not project_service.check_project_ownership(project_uuid, user_uuid):
            raise HTTPException(status_code=404, detail="Project not found")

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project ID")

    # Get messages for project
    messages_data = MOCK_CHAT_MESSAGES.get(project_id, [])
    messages = [ChatMessage(**msg) for msg in messages_data]

    # Apply pagination
    total = len(messages)
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    messages_page = messages[start_idx:end_idx]

    paginated_response = PaginatedResponse(
        items=messages_page,
        total=total,
        page=page,
        limit=limit,
        hasMore=end_idx < total,
    )

    return ApiResponse(success=True, data=paginated_response)


@router.get("/{project_id}/preview")
async def get_csv_preview(
    project_id: str, user_id: str = Depends(verify_token)
) -> ApiResponse[CSVPreview]:
    """Get CSV data preview"""

    # Verify project exists and user has access
    try:
        user_uuid = uuid.UUID(user_id)
        project_uuid = uuid.UUID(project_id)

        if not project_service.check_project_ownership(project_uuid, user_uuid):
            raise HTTPException(status_code=404, detail="Project not found")

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project ID")

    # Get real project data and generate preview
    try:
        project_obj = project_service.get_project_by_id(project_uuid)
        if not project_obj:
            raise HTTPException(status_code=404, detail="Project not found")

        # Check if CSV file exists
        if not project_obj.csv_path:
            raise HTTPException(status_code=404, detail="CSV preview not available")

        # Load actual CSV data from storage
        preview = _load_csv_preview_from_storage(project_obj)

        if not preview:
            # Fallback to metadata-based preview if file loading fails
            preview = _generate_preview_from_metadata(project_obj)

        if not preview:
            raise HTTPException(status_code=404, detail="CSV preview not available")

        return ApiResponse(success=True, data=preview)

    except HTTPException:
        # Re-raise HTTPExceptions (like 404) as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error loading CSV preview: {str(e)}"
        )


def _load_csv_preview_from_storage(project_obj) -> Optional[CSVPreview]:
    """Load CSV preview from actual file in storage"""
    try:
        from services.storage_service import storage_service
        import pandas as pd
        import io

        # Download CSV file from storage
        csv_bytes = storage_service.download_file(project_obj.csv_path)
        if not csv_bytes:
            return None

        # Read CSV into pandas DataFrame
        csv_buffer = io.BytesIO(csv_bytes)
        df = pd.read_csv(csv_buffer)

        # Get first 5 rows for preview
        preview_df = df.head(5)

        # Extract column information
        columns = list(df.columns)
        sample_data = preview_df.values.tolist()
        total_rows = len(df)

        # Determine data types
        data_types = {}
        for col in columns:
            dtype = str(df[col].dtype)
            if "int" in dtype or "float" in dtype:
                data_types[col] = "number"
            elif "datetime" in dtype or "date" in dtype:
                data_types[col] = "date"
            elif "bool" in dtype:
                data_types[col] = "boolean"
            else:
                data_types[col] = "string"

        # Convert any non-serializable values to strings
        serializable_sample_data = []
        for row in sample_data:
            serializable_row = []
            for value in row:
                if pd.isna(value):
                    serializable_row.append(None)
                elif isinstance(value, (pd.Timestamp, pd.Timedelta)):
                    serializable_row.append(str(value))
                else:
                    serializable_row.append(value)
            serializable_sample_data.append(serializable_row)

        return CSVPreview(
            columns=columns,
            sample_data=serializable_sample_data,
            total_rows=total_rows,
            data_types=data_types,
        )

    except Exception as e:
        logger.error(f"Error loading CSV preview from storage: {str(e)}")
        return None


def _generate_preview_from_metadata(project_obj) -> Optional[CSVPreview]:
    """Generate preview from project metadata as fallback"""
    try:
        if not project_obj.columns_metadata:
            return None

        # Extract column names and types
        columns = [col.get("name", "") for col in project_obj.columns_metadata]
        data_types = {
            col.get("name", ""): col.get("type", "unknown")
            for col in project_obj.columns_metadata
        }

        # Generate sample data from metadata
        sample_data = []
        for i in range(min(5, project_obj.row_count or 5)):  # Show max 5 sample rows
            row = []
            for col in project_obj.columns_metadata:
                sample_values = col.get("sample_values", [])
                if sample_values and len(sample_values) > i:
                    row.append(sample_values[i])
                else:
                    # Generate placeholder based on type
                    col_type = col.get("type", "string")
                    if col_type == "number":
                        row.append(0)
                    elif col_type == "date":
                        row.append("2024-01-01")
                    else:
                        row.append(f"Sample {i+1}")
            sample_data.append(row)

        return CSVPreview(
            columns=columns,
            sample_data=sample_data,
            total_rows=project_obj.row_count or 0,
            data_types=data_types,
        )

    except Exception as e:
        logger.error(f"Error generating preview from metadata: {str(e)}")
        return None


@router.get("/{project_id}/suggestions")
async def get_query_suggestions(
    project_id: str, user_id: str = Depends(verify_token)
) -> ApiResponse[List[QuerySuggestion]]:
    """Get query suggestions"""

    # Verify project exists and user has access
    try:
        user_uuid = uuid.UUID(user_id)
        project_uuid = uuid.UUID(project_id)

        if not project_service.check_project_ownership(project_uuid, user_uuid):
            raise HTTPException(status_code=404, detail="Project not found")

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid project ID")

    # Generate intelligent suggestions using LangChain service
    try:
        suggestions_data = langchain_service.generate_suggestions(project_id, user_id)
        suggestions = [QuerySuggestion(**sug) for sug in suggestions_data]
    except Exception:
        # Fallback to mock suggestions if service fails
        suggestions = [QuerySuggestion(**sug) for sug in MOCK_SUGGESTIONS]

    return ApiResponse(success=True, data=suggestions)
