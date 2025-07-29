import uuid
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from main import app
from middleware.auth_middleware import verify_token
from models.project import ProjectCreate, ProjectStatusEnum
from models.user import GoogleOAuthData, UserInDB
from services.auth_service import AuthService
from services.langchain_service import LangChainService, langchain_service
from services.project_service import get_project_service
from services.user_service import get_user_service

client = TestClient(app)

# Initialize services for testing
auth_service = AuthService()
project_service = get_project_service()
user_service = get_user_service()


def mock_verify_token():
    """Mock verify_token that returns test user UUID as string"""
    return "00000000-0000-0000-0000-000000000001"


@pytest.fixture
def sample_user():
    """Sample user for testing"""
    test_user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
    return UserInDB(
        id=test_user_id,
        email="test@example.com",
        name="Test User",
        avatar_url="https://example.com/avatar.jpg",
        google_id="google_123",
        is_active=True,
        is_verified=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def test_access_token(sample_user):
    """Create a valid access token for testing"""
    return auth_service.create_access_token(str(sample_user.id), sample_user.email)


@pytest.fixture
def test_user_in_db(sample_user):
    """Ensure test user exists in database"""
    try:
        user_service.create_user_from_google(
            google_data=GoogleOAuthData(
                google_id=sample_user.google_id,
                email=sample_user.email,
                name=sample_user.name,
                avatar_url=sample_user.avatar_url,
            )
        )
    except Exception:
        pass
    return sample_user


@pytest.fixture
def test_project_with_metadata(test_user_in_db):
    """Create a test project with CSV metadata"""
    project_data = ProjectCreate(
        name="Sales Analysis Dataset", description="Test project with metadata"
    )
    project = project_service.create_project(project_data, test_user_in_db.id)

    # Mock project with metadata
    project_dict = {
        "id": str(project.id),
        "name": "Sales Analysis Dataset",
        "row_count": 1000,
        "column_count": 8,
        "columns_metadata": [
            {
                "name": "date",
                "type": "date",
                "nullable": False,
                "sample_values": ["2024-01-01", "2024-01-02", "2024-01-03"],
            },
            {
                "name": "product_name",
                "type": "string",
                "nullable": False,
                "sample_values": ["Product A", "Product B", "Product C"],
            },
            {
                "name": "sales_amount",
                "type": "number",
                "nullable": False,
                "sample_values": [1500.00, 2300.50, 1890.25],
            },
            {
                "name": "quantity",
                "type": "number",
                "nullable": False,
                "sample_values": [10, 15, 12],
            },
            {
                "name": "category",
                "type": "string",
                "nullable": False,
                "sample_values": ["Electronics", "Clothing", "Home"],
            },
            {
                "name": "region",
                "type": "string",
                "nullable": False,
                "sample_values": ["North", "South", "East"],
            },
        ],
    }
    return project_dict


@pytest.fixture
def mock_langchain_service():
    """Mock the LangChain service for testing"""
    mock_service = Mock(spec=LangChainService)
    return mock_service


class TestLangChainChatIntegration:
    """Test LangChain chat endpoint integration"""

    def test_sql_query_processing(
        self,
        test_client,
        test_access_token,
        test_user_in_db,
        test_project_with_metadata,
    ):
        """Test SQL query processing through LangChain"""
        app.dependency_overrides[verify_token] = mock_verify_token

        with patch("services.langchain_service.langchain_service") as mock_service:
            # Mock LangChain service response
            mock_service.process_query.return_value = Mock(
                id="qr_test_123",
                query="Show me total sales by product",
                sql_query="SELECT product_name, SUM(sales_amount) as total_sales FROM data GROUP BY product_name ORDER BY total_sales DESC",
                result_type="table",
                data=[
                    {"product_name": "Product A", "total_sales": 15000.50},
                    {"product_name": "Product B", "total_sales": 12300.25},
                ],
                execution_time=0.5,
                row_count=2,
                chart_config=None,
                error=None,
                summary=None,
            )

            try:
                response = test_client.post(
                    f"/chat/{test_project_with_metadata['id']}/message",
                    json={"message": "Show me total sales by product"},
                    headers={"Authorization": f"Bearer {test_access_token}"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert "message" in data["data"]
                assert "result" in data["data"]

                result = data["data"]["result"]
                assert result["result_type"] == "table"
                assert result["sql_query"] is not None
                assert result["row_count"] == 2
                assert len(result["data"]) == 2

                # Verify LangChain service was called
                mock_service.process_query.assert_called_once()

            finally:
                app.dependency_overrides.clear()

    def test_chart_query_processing(
        self,
        test_client,
        test_access_token,
        test_user_in_db,
        test_project_with_metadata,
    ):
        """Test chart query processing through LangChain"""
        app.dependency_overrides[verify_token] = mock_verify_token

        with patch("services.langchain_service.langchain_service") as mock_service:
            # Mock chart response
            mock_service.process_query.return_value = Mock(
                id="qr_chart_123",
                query="Create a bar chart of sales by category",
                sql_query="SELECT category, SUM(sales_amount) as total_sales FROM data GROUP BY category",
                result_type="chart",
                data=[
                    {"category": "Electronics", "total_sales": 45000.50},
                    {"category": "Clothing", "total_sales": 32300.25},
                ],
                execution_time=0.7,
                row_count=2,
                chart_config={
                    "type": "bar",
                    "x_axis": "category",
                    "y_axis": "total_sales",
                    "title": "Sales by Category",
                },
                error=None,
                summary=None,
            )

            try:
                response = test_client.post(
                    f"/chat/{test_project_with_metadata['id']}/message",
                    json={"message": "Create a bar chart of sales by category"},
                    headers={"Authorization": f"Bearer {test_access_token}"},
                )

                assert response.status_code == 200
                data = response.json()
                result = data["data"]["result"]

                assert result["result_type"] == "chart"
                assert result["chart_config"] is not None
                assert result["chart_config"]["type"] == "bar"
                assert result["chart_config"]["x_axis"] == "category"
                assert result["chart_config"]["y_axis"] == "total_sales"

            finally:
                app.dependency_overrides.clear()

    def test_general_query_processing(
        self,
        test_client,
        test_access_token,
        test_user_in_db,
        test_project_with_metadata,
    ):
        """Test general query processing through LangChain"""
        app.dependency_overrides[verify_token] = mock_verify_token

        with patch("services.langchain_service.langchain_service") as mock_service:
            # Mock general response
            mock_service.process_query.return_value = Mock(
                id="qr_general_123",
                query="What can you tell me about this dataset?",
                sql_query=None,
                result_type="summary",
                data=None,
                execution_time=0.3,
                row_count=0,
                chart_config=None,
                error=None,
                summary="This is a sales dataset with 1000 rows and 6 columns including date, product information, sales amounts, and regional data. You can ask questions about sales trends, product performance, or regional analysis.",
            )

            try:
                response = test_client.post(
                    f"/chat/{test_project_with_metadata['id']}/message",
                    json={"message": "What can you tell me about this dataset?"},
                    headers={"Authorization": f"Bearer {test_access_token}"},
                )

                assert response.status_code == 200
                data = response.json()
                result = data["data"]["result"]

                assert result["result_type"] == "summary"
                assert result["summary"] is not None
                assert "1000 rows" in result["summary"]

            finally:
                app.dependency_overrides.clear()

    def test_error_handling_with_fallback(
        self,
        test_client,
        test_access_token,
        test_user_in_db,
        test_project_with_metadata,
    ):
        """Test error handling with fallback to mock data"""
        app.dependency_overrides[verify_token] = mock_verify_token

        with patch("services.langchain_service.langchain_service") as mock_service:
            # Mock service error
            mock_service.process_query.side_effect = Exception(
                "LangChain service unavailable"
            )

            try:
                response = test_client.post(
                    f"/chat/{test_project_with_metadata['id']}/message",
                    json={"message": "Show me total sales"},
                    headers={"Authorization": f"Bearer {test_access_token}"},
                )

                assert response.status_code == 200
                data = response.json()

                # Should fallback to mock logic
                assert data["success"] is True
                assert "result" in data["data"]
                result = data["data"]["result"]
                assert result["result_type"] in ["table", "chart", "summary"]

            finally:
                app.dependency_overrides.clear()

    def test_intelligent_suggestions(
        self,
        test_client,
        test_access_token,
        test_user_in_db,
        test_project_with_metadata,
    ):
        """Test intelligent suggestions generation"""
        app.dependency_overrides[verify_token] = mock_verify_token

        with patch("services.langchain_service.langchain_service") as mock_service:
            # Mock intelligent suggestions
            mock_service.generate_suggestions.return_value = [
                {
                    "id": "sug_sales_total",
                    "text": "Show me the total sales_amount",
                    "category": "analysis",
                    "complexity": "beginner",
                },
                {
                    "id": "sug_sales_by_category",
                    "text": "Break down sales_amount by category",
                    "category": "analysis",
                    "complexity": "intermediate",
                },
                {
                    "id": "sug_chart_category",
                    "text": "Create a bar chart of sales_amount by category",
                    "category": "visualization",
                    "complexity": "intermediate",
                },
            ]

            try:
                response = test_client.get(
                    f"/chat/{test_project_with_metadata['id']}/suggestions",
                    headers={"Authorization": f"Bearer {test_access_token}"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert len(data["data"]) == 3

                suggestions = data["data"]
                assert suggestions[0]["text"] == "Show me the total sales_amount"
                assert suggestions[1]["category"] == "analysis"
                assert suggestions[2]["complexity"] == "intermediate"

                # Verify service was called
                mock_service.generate_suggestions.assert_called_once()

            finally:
                app.dependency_overrides.clear()

    def test_suggestions_fallback(
        self,
        test_client,
        test_access_token,
        test_user_in_db,
        test_project_with_metadata,
    ):
        """Test suggestions fallback to mock data"""
        app.dependency_overrides[verify_token] = mock_verify_token

        with patch("services.langchain_service.langchain_service") as mock_service:
            # Mock service error for suggestions
            mock_service.generate_suggestions.side_effect = Exception("Service error")

            try:
                response = test_client.get(
                    f"/chat/{test_project_with_metadata['id']}/suggestions",
                    headers={"Authorization": f"Bearer {test_access_token}"},
                )

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True

                # Should fallback to mock suggestions
                assert len(data["data"]) > 0
                assert all("text" in suggestion for suggestion in data["data"])

            finally:
                app.dependency_overrides.clear()

    def test_ai_response_formatting(
        self,
        test_client,
        test_access_token,
        test_user_in_db,
        test_project_with_metadata,
    ):
        """Test AI response content formatting based on result type"""
        app.dependency_overrides[verify_token] = mock_verify_token

        test_cases = [
            {
                "result_type": "table",
                "expected_content": "I found 2 results for your query",
            },
            {
                "result_type": "chart",
                "expected_content": "I've created a bar visualization",
            },
            {
                "result_type": "summary",
                "expected_content": "This is a summary response",
            },
            {
                "result_type": "error",
                "expected_content": "I encountered an error",
            },
        ]

        for case in test_cases:
            with patch("services.langchain_service.langchain_service") as mock_service:
                mock_result = Mock(
                    result_type=case["result_type"],
                    row_count=2 if case["result_type"] == "table" else 0,
                    chart_config=(
                        {"type": "bar"} if case["result_type"] == "chart" else None
                    ),
                    summary=(
                        "This is a summary response"
                        if case["result_type"] == "summary"
                        else None
                    ),
                    error=(
                        "Test error message" if case["result_type"] == "error" else None
                    ),
                    sql_query=(
                        "SELECT * FROM data"
                        if case["result_type"] in ["table", "chart"]
                        else None
                    ),
                )
                mock_service.process_query.return_value = mock_result

                try:
                    response = test_client.post(
                        f"/chat/{test_project_with_metadata['id']}/message",
                        json={"message": "Test query"},
                        headers={"Authorization": f"Bearer {test_access_token}"},
                    )

                    assert response.status_code == 200
                    data = response.json()
                    ai_message = data["data"]["message"]

                    # Check AI response content contains expected text
                    assert case["expected_content"].split()[0] in ai_message["content"]

                finally:
                    app.dependency_overrides.clear()


class TestLangChainServiceUnit:
    """Unit tests for LangChain service components"""

    def test_query_classification(self):
        """Test query type classification"""
        from services.langchain_service import QueryTypeClassifierTool

        classifier = QueryTypeClassifierTool()

        # SQL queries
        assert classifier.run("Show me total sales") == "sql"
        assert classifier.run("Count the number of rows") == "sql"
        assert classifier.run("What's the average price?") == "sql"

        # Chart queries
        assert classifier.run("Create a bar chart") == "chart"
        assert classifier.run("Show me a visualization") == "chart"
        assert classifier.run("Plot sales over time") == "chart"

        # Mixed queries (chart takes precedence)
        assert classifier.run("Show me total sales in a chart") == "chart"

        # General queries
        assert classifier.run("What is this dataset about?") == "general"
        assert classifier.run("Help me understand the data") == "general"

    @patch("services.langchain_service.ChatOpenAI")
    def test_sql_generation_tool(self, mock_chat_openai):
        """Test SQL generation tool"""
        from services.langchain_service import SQLGenerationTool

        # Mock OpenAI response
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = (
            "SELECT product_name, SUM(sales_amount) FROM data GROUP BY product_name"
        )
        mock_llm.invoke.return_value = mock_response
        mock_chat_openai.return_value = mock_llm

        tool = SQLGenerationTool()

        schema_info = """
        CSV Schema:
        - product_name (string)
        - sales_amount (number)
        """

        result = tool.run("Show me total sales by product", schema_info)

        assert "SELECT" in result
        assert "product_name" in result
        assert "sales_amount" in result
        mock_llm.invoke.assert_called_once()

    def test_schema_info_extraction(self):
        """Test schema information extraction from project metadata"""
        mock_project = {
            "columns_metadata": [
                {
                    "name": "date",
                    "type": "date",
                    "sample_values": ["2024-01-01", "2024-01-02"],
                },
                {
                    "name": "sales",
                    "type": "number",
                    "sample_values": [1500.0, 2300.5],
                },
            ]
        }

        service = LangChainService()
        schema_info = service._get_schema_info(mock_project)

        assert "CSV Schema:" in schema_info
        assert "date (date)" in schema_info
        assert "sales (number)" in schema_info
        assert "2024-01-01" in schema_info
        assert "1500.0" in schema_info

    def test_mock_data_generation(self):
        """Test mock data generation based on query content"""
        service = LangChainService()

        # Sales chart query
        mock_data = service._generate_mock_data("sales chart", "chart")
        assert "chart_config" in mock_data
        assert mock_data["chart_config"]["type"] == "bar"
        assert "category" in mock_data["data"][0]

        # Total/sum query
        mock_data = service._generate_mock_data("total sales", "table")
        assert "product_name" in mock_data["data"][0]
        assert "total_sales" in mock_data["data"][0]

        # General query
        mock_data = service._generate_mock_data("general question", "table")
        assert "date" in mock_data["data"][0]
        assert "value" in mock_data["data"][0]

    def test_error_result_creation(self):
        """Test error result creation"""
        service = LangChainService()

        error_result = service._create_error_result("test query", "Test error message")

        assert error_result.result_type == "error"
        assert error_result.error == "Test error message"
        assert error_result.query == "test query"
        assert error_result.execution_time == 0.0
        assert error_result.row_count == 0


def test_langchain_service_initialization():
    """Test LangChain service initialization"""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        with patch("services.langchain_service.ChatOpenAI"):
            with patch("services.langchain_service.initialize_agent"):
                service = LangChainService()
                assert service.openai_api_key == "test-key"
                assert len(service.tools) == 2  # SQL tool and classifier tool


def test_langchain_service_missing_api_key():
    """Test LangChain service initialization without API key"""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(
            ValueError, match="OPENAI_API_KEY environment variable not set"
        ):
            LangChainService()
