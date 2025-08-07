"""
LangChain Service Integration Tests - Task B26

Tests the integration between LangChain service, embeddings service, suggestions service,
and DuckDB service to ensure AI-powered query processing works correctly.
"""

import uuid
from unittest.mock import Mock, patch

import pytest

from models.project import ProjectCreate
from models.response_schemas import QueryResult
from models.user import GoogleOAuthData
from services.duckdb_service import DuckDBService
from services.embeddings_service import EmbeddingsService
from services.langchain_service import LangChainService
from services.project_service import get_project_service
from services.suggestions_service import SuggestionsService
from services.user_service import get_user_service


class TestLangChainIntegration:
    """Integration tests for LangChain service with other AI services"""

    def test_langchain_service_initialization(self):
        """Test that LangChain service initializes correctly"""
        langchain_service = LangChainService()
        assert langchain_service is not None

        # Test that service components are accessible
        assert hasattr(langchain_service, "process_query")
        assert hasattr(langchain_service, "generate_suggestions")

    @patch("services.langchain_service.OpenAI")
    def test_langchain_query_processing_integration(self, mock_openai, test_db_setup):
        """Test query processing integration across AI services"""
        user_service = get_user_service()
        project_service = get_project_service()
        langchain_service = LangChainService()

        # Mock OpenAI responses
        mock_llm = Mock()
        mock_llm.invoke.return_value.content = "SELECT * FROM data LIMIT 5"
        mock_openai.return_value = mock_llm

        # Create test user and project
        google_data = GoogleOAuthData(
            google_id="langchain_test_1",
            email="langchain@test.com",
            name="LangChain Test User",
        )
        test_user, _ = user_service.create_or_update_from_google_oauth(google_data)

        project_data = ProjectCreate(
            name="LangChain Test Project", description="Testing LangChain integration"
        )
        test_project = project_service.create_project(project_data, test_user.id)

        # Update project with test metadata
        test_metadata = [
            {
                "name": "name",
                "type": "string",
                "nullable": False,
                "sample_values": ["John", "Jane", "Bob"],
            },
            {
                "name": "age",
                "type": "number",
                "nullable": False,
                "sample_values": [25, 30, 35],
            },
        ]

        project_service.update_project_metadata(
            test_project.id,
            row_count=100,
            column_count=2,
            columns_metadata=test_metadata,
            csv_filename="test.csv",
            csv_path="test/path/test.csv",
        )
        project_service.update_project_status(test_project.id, "ready")

        # Mock DuckDB service
        with patch("services.langchain_service.DuckDBService") as mock_duckdb_class:
            mock_duckdb = Mock()
            mock_duckdb.execute_query.return_value = {
                "data": [{"name": "John", "age": 25}, {"name": "Jane", "age": 30}],
                "execution_time": 0.1,
                "row_count": 2,
            }
            mock_duckdb_class.return_value = mock_duckdb

            # Test query processing
            result = langchain_service.process_query(
                test_project.id, "Show me all the data"
            )

            assert isinstance(result, QueryResult)
            assert result.query == "Show me all the data"
            assert result.result_type in ["table", "chart", "summary", "error"]
            assert result.execution_time >= 0

        # Clean up
        project_service.delete_project(test_project.id)
        user_service.delete_user(test_user.id)

    @patch("services.embeddings_service.OpenAI")
    def test_embeddings_integration(self, mock_openai, test_db_setup):
        """Test embeddings service integration with LangChain"""
        user_service = get_user_service()
        project_service = get_project_service()
        embeddings_service = EmbeddingsService()

        # Mock OpenAI embeddings
        mock_client = Mock()
        mock_client.embeddings.create.return_value.data = [Mock(embedding=[0.1] * 1536)]
        mock_openai.return_value = mock_client

        # Create test user and project
        google_data = GoogleOAuthData(
            google_id="embeddings_test_1",
            email="embeddings@test.com",
            name="Embeddings Test User",
        )
        test_user, _ = user_service.create_or_update_from_google_oauth(google_data)

        project_data = ProjectCreate(
            name="Embeddings Test Project", description="Testing embeddings integration"
        )
        test_project = project_service.create_project(project_data, test_user.id)

        # Update project with metadata
        test_metadata = [
            {
                "name": "product_name",
                "type": "string",
                "nullable": False,
                "sample_values": ["Widget A", "Widget B", "Widget C"],
            }
        ]

        project_service.update_project_metadata(
            test_project.id,
            row_count=50,
            column_count=1,
            columns_metadata=test_metadata,
            csv_filename="products.csv",
            csv_path="test/products.csv",
        )

        # Test embeddings generation
        project_db = project_service.get_project_by_id(test_project.id)
        embeddings = embeddings_service.generate_embeddings_for_project(project_db)

        assert embeddings is not None
        assert len(embeddings) > 0

        # Test semantic search
        search_results = embeddings_service.semantic_search(
            test_project.id, "product information", top_k=5
        )

        assert isinstance(search_results, list)

        # Clean up
        project_service.delete_project(test_project.id)
        user_service.delete_user(test_user.id)

    def test_suggestions_service_integration(self, test_db_setup):
        """Test suggestions service integration with project data"""
        user_service = get_user_service()
        project_service = get_project_service()
        suggestions_service = SuggestionsService()

        # Create test user and project
        google_data = GoogleOAuthData(
            google_id="suggestions_test_1",
            email="suggestions@test.com",
            name="Suggestions Test User",
        )
        test_user, _ = user_service.create_or_update_from_google_oauth(google_data)

        project_data = ProjectCreate(
            name="Suggestions Test Project",
            description="Testing suggestions integration",
        )
        test_project = project_service.create_project(project_data, test_user.id)

        # Update project with rich metadata
        test_metadata = [
            {
                "name": "sales_amount",
                "type": "number",
                "nullable": False,
                "sample_values": [1000, 1500, 2000],
            },
            {
                "name": "region",
                "type": "string",
                "nullable": False,
                "sample_values": ["North", "South", "East", "West"],
            },
            {
                "name": "date",
                "type": "date",
                "nullable": False,
                "sample_values": ["2024-01-01", "2024-01-02", "2024-01-03"],
            },
        ]

        project_service.update_project_metadata(
            test_project.id,
            row_count=1000,
            column_count=3,
            columns_metadata=test_metadata,
            csv_filename="sales.csv",
            csv_path="test/sales.csv",
        )

        # Test suggestions generation
        project_db = project_service.get_project_by_id(test_project.id)
        suggestions = suggestions_service.generate_suggestions(project_db, limit=10)

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

        # Verify suggestion structure
        for suggestion in suggestions[:3]:  # Check first few suggestions
            assert "id" in suggestion
            assert "text" in suggestion
            assert "category" in suggestion
            assert "complexity" in suggestion
            assert suggestion["category"] in [
                "analysis",
                "visualization",
                "summary",
                "filter",
            ]
            assert suggestion["complexity"] in ["beginner", "intermediate", "advanced"]

        # Clean up
        project_service.delete_project(test_project.id)
        user_service.delete_user(test_user.id)

    @patch("services.langchain_service.DuckDBService")
    def test_duckdb_integration(self, mock_duckdb_class, test_db_setup):
        """Test DuckDB service integration with LangChain"""
        user_service = get_user_service()
        project_service = get_project_service()

        # Mock DuckDB service
        mock_duckdb = Mock()
        mock_duckdb.execute_query.return_value = {
            "data": [
                {"product": "Widget A", "sales": 1000},
                {"product": "Widget B", "sales": 1500},
                {"product": "Widget C", "sales": 2000},
            ],
            "execution_time": 0.05,
            "row_count": 3,
        }
        mock_duckdb_class.return_value = mock_duckdb

        # Create test user and project
        google_data = GoogleOAuthData(
            google_id="duckdb_test_1", email="duckdb@test.com", name="DuckDB Test User"
        )
        test_user, _ = user_service.create_or_update_from_google_oauth(google_data)

        project_data = ProjectCreate(
            name="DuckDB Test Project", description="Testing DuckDB integration"
        )
        test_project = project_service.create_project(project_data, test_user.id)

        # Test DuckDB service creation and query execution
        duckdb_service = DuckDBService()

        # Mock CSV data for DuckDB
        with patch(
            "services.storage_service.storage_service.download_file"
        ) as mock_download:
            mock_download.return_value = (
                b"product,sales\nWidget A,1000\nWidget B,1500\nWidget C,2000"
            )

            # Test query execution
            result = duckdb_service.execute_query(
                test_project.id, "SELECT * FROM data ORDER BY sales DESC"
            )

            assert isinstance(result, dict)
            assert "data" in result
            assert "execution_time" in result
            assert "row_count" in result
            assert result["row_count"] == 3

        # Clean up
        project_service.delete_project(test_project.id)
        user_service.delete_user(test_user.id)

    @patch("services.langchain_service.OpenAI")
    @patch("services.embeddings_service.OpenAI")
    def test_end_to_end_ai_workflow(
        self, mock_embeddings_openai, mock_langchain_openai, test_db_setup
    ):
        """Test complete AI workflow integration"""
        user_service = get_user_service()
        project_service = get_project_service()
        langchain_service = LangChainService()
        embeddings_service = EmbeddingsService()
        suggestions_service = SuggestionsService()

        # Mock OpenAI services
        mock_llm = Mock()
        mock_llm.invoke.return_value.content = "SELECT product, SUM(sales) as total_sales FROM data GROUP BY product ORDER BY total_sales DESC"
        mock_langchain_openai.return_value = mock_llm

        mock_embeddings_client = Mock()
        mock_embeddings_client.embeddings.create.return_value.data = [
            Mock(embedding=[0.1] * 1536)
        ]
        mock_embeddings_openai.return_value = mock_embeddings_client

        # Create test user and project
        google_data = GoogleOAuthData(
            google_id="workflow_test_1",
            email="workflow@test.com",
            name="Workflow Test User",
        )
        test_user, _ = user_service.create_or_update_from_google_oauth(google_data)

        project_data = ProjectCreate(
            name="Workflow Test Project", description="Testing end-to-end AI workflow"
        )
        test_project = project_service.create_project(project_data, test_user.id)

        # Update project with comprehensive metadata
        test_metadata = [
            {
                "name": "product",
                "type": "string",
                "nullable": False,
                "sample_values": ["Laptop", "Mouse", "Keyboard"],
            },
            {
                "name": "sales",
                "type": "number",
                "nullable": False,
                "sample_values": [50000, 1200, 800],
            },
            {
                "name": "quarter",
                "type": "string",
                "nullable": False,
                "sample_values": ["Q1", "Q2", "Q3", "Q4"],
            },
        ]

        project_service.update_project_metadata(
            test_project.id,
            row_count=500,
            column_count=3,
            columns_metadata=test_metadata,
            csv_filename="sales_data.csv",
            csv_path="test/sales_data.csv",
        )
        project_service.update_project_status(test_project.id, "ready")

        # Step 1: Generate embeddings for the project
        project_db = project_service.get_project_by_id(test_project.id)
        embeddings = embeddings_service.generate_embeddings_for_project(project_db)
        assert embeddings is not None

        # Step 2: Generate suggestions
        suggestions = suggestions_service.generate_suggestions(project_db, limit=5)
        assert len(suggestions) > 0

        # Step 3: Process a complex query through LangChain
        with patch("services.langchain_service.DuckDBService") as mock_duckdb_class:
            mock_duckdb = Mock()
            mock_duckdb.execute_query.return_value = {
                "data": [
                    {"product": "Laptop", "total_sales": 150000},
                    {"product": "Mouse", "total_sales": 12000},
                    {"product": "Keyboard", "total_sales": 8000},
                ],
                "execution_time": 0.15,
                "row_count": 3,
            }
            mock_duckdb_class.return_value = mock_duckdb

            # Process query
            query_result = langchain_service.process_query(
                test_project.id, "What are the total sales by product?"
            )

            assert isinstance(query_result, QueryResult)
            assert query_result.query == "What are the total sales by product?"
            assert query_result.result_type in ["table", "chart", "summary", "error"]

        # Step 4: Test semantic search integration
        search_results = embeddings_service.semantic_search(
            test_project.id, "product sales analysis", top_k=3
        )

        assert isinstance(search_results, list)

        # Clean up
        project_service.delete_project(test_project.id)
        user_service.delete_user(test_user.id)

    def test_ai_service_error_handling_integration(self, test_db_setup):
        """Test error handling across AI services"""
        user_service = get_user_service()
        project_service = get_project_service()
        langchain_service = LangChainService()

        # Create test user and project
        google_data = GoogleOAuthData(
            google_id="error_handling_test",
            email="errorhandling@test.com",
            name="Error Handling Test User",
        )
        test_user, _ = user_service.create_or_update_from_google_oauth(google_data)

        project_data = ProjectCreate(
            name="Error Handling Test Project",
            description="Testing AI service error handling",
        )
        test_project = project_service.create_project(project_data, test_user.id)

        # Test query processing with invalid project (no metadata)
        with patch("services.langchain_service.OpenAI") as mock_openai:
            # Mock OpenAI to raise an exception
            mock_llm = Mock()
            mock_llm.invoke.side_effect = Exception("API Error")
            mock_openai.return_value = mock_llm

            # Query processing should handle errors gracefully
            result = langchain_service.process_query(test_project.id, "Invalid query")

            # Should return error result, not raise exception
            assert isinstance(result, QueryResult)
            assert result.result_type == "error"
            assert result.error is not None

        # Clean up
        project_service.delete_project(test_project.id)
        user_service.delete_user(test_user.id)

    def test_ai_service_configuration_validation(self):
        """Test that AI services are properly configured for integration"""
        # Test LangChain service
        langchain_service = LangChainService()
        assert hasattr(langchain_service, "process_query")
        assert hasattr(langchain_service, "generate_suggestions")

        # Test embeddings service
        embeddings_service = EmbeddingsService()
        assert hasattr(embeddings_service, "generate_embeddings_for_project")
        assert hasattr(embeddings_service, "semantic_search")

        # Test suggestions service
        suggestions_service = SuggestionsService()
        assert hasattr(suggestions_service, "generate_suggestions")

        # Test DuckDB service
        duckdb_service = DuckDBService()
        assert hasattr(duckdb_service, "execute_query")
