import uuid
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch
import pytest

from services.embeddings_service import EmbeddingsService, get_embeddings_service


class TestEmbeddingsService:
    """Test embeddings service functionality"""

    def test_embeddings_service_initialization(self):
        """Test embeddings service initialization"""
        # Test with API key available
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            with patch("services.embeddings_service.OpenAI") as mock_openai:
                service = EmbeddingsService()
                assert service.openai_api_key == "test-key"
                assert service.embedding_model == "text-embedding-3-small"
                mock_openai.assert_called_once()

    def test_embeddings_service_no_api_key(self):
        """Test embeddings service initialization without API key"""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY environment variable not set"):
                EmbeddingsService()

    def test_embeddings_service_testing_mode(self):
        """Test embeddings service initialization in testing mode"""
        with patch.dict("os.environ", {"TESTING": "true"}, clear=True):
            service = EmbeddingsService()
            assert service.client is None
            assert service.openai_api_key is None

    @patch("services.embeddings_service.OpenAI")
    def test_generate_embedding_success(self, mock_openai_class):
        """Test successful embedding generation"""
        # Mock OpenAI client and response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3, 0.4, 0.5])]
        mock_client.embeddings.create.return_value = mock_response
        mock_openai_class.return_value = mock_client

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            service = EmbeddingsService()
            service.client = mock_client

            result = service.generate_embedding("test text")

            assert result == [0.1, 0.2, 0.3, 0.4, 0.5]
            mock_client.embeddings.create.assert_called_once_with(
                model="text-embedding-3-small",
                input="test text"
            )

    def test_generate_embedding_no_client(self):
        """Test embedding generation without OpenAI client"""
        with patch.dict("os.environ", {"TESTING": "true"}, clear=True):
            service = EmbeddingsService()
            result = service.generate_embedding("test text")
            assert result is None

    def test_generate_embedding_empty_text(self):
        """Test embedding generation with empty text"""
        with patch.dict("os.environ", {"TESTING": "true"}, clear=True):
            service = EmbeddingsService()
            
            result = service.generate_embedding("")
            assert result is None
            
            result = service.generate_embedding("   ")
            assert result is None

    @patch("services.embeddings_service.OpenAI")
    def test_generate_embedding_api_error(self, mock_openai_class):
        """Test embedding generation with API error"""
        mock_client = Mock()
        mock_client.embeddings.create.side_effect = Exception("API Error")
        mock_openai_class.return_value = mock_client

        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            service = EmbeddingsService()
            service.client = mock_client

            result = service.generate_embedding("test text")
            assert result is None

    def test_generate_project_embeddings(self):
        """Test project embeddings generation"""
        service = EmbeddingsService()
        
        # Mock dependencies
        mock_project = Mock()
        mock_project.name = "Sales Dataset"
        mock_project.description = "Customer sales data"
        mock_project.row_count = 1000
        mock_project.column_count = 4
        mock_project.columns_metadata = [
            {
                "name": "customer_id",
                "type": "number",
                "sample_values": [1, 2, 3]
            },
            {
                "name": "product_name",
                "type": "string",
                "sample_values": ["Product A", "Product B", "Product C"]
            }
        ]
        
        service.project_service = Mock()
        service.project_service.check_project_ownership.return_value = True
        service.project_service.get_project_by_id.return_value = mock_project
        
        # Mock embedding generation
        service.generate_embedding = Mock(return_value=[0.1, 0.2, 0.3])
        
        project_id = "12345678-1234-5678-9012-123456789012"
        user_id = "87654321-4321-8765-2109-876543210987"
        result = service.generate_project_embeddings(project_id, user_id)
        
        assert result is True
        # Should generate embeddings for overview, columns, and sample data
        assert service.generate_embedding.call_count >= 3

    def test_generate_project_embeddings_no_access(self):
        """Test project embeddings generation without access"""
        service = EmbeddingsService()
        
        service.project_service = Mock()
        service.project_service.check_project_ownership.return_value = False
        
        result = service.generate_project_embeddings("12345678-1234-5678-9012-123456789012", "87654321-4321-8765-2109-876543210987")
        assert result is False

    def test_generate_project_embeddings_no_metadata(self):
        """Test project embeddings generation without metadata"""
        service = EmbeddingsService()
        
        mock_project = Mock()
        mock_project.columns_metadata = None
        
        service.project_service = Mock()
        service.project_service.check_project_ownership.return_value = True
        service.project_service.get_project_by_id.return_value = mock_project
        
        result = service.generate_project_embeddings("12345678-1234-5678-9012-123456789012", "87654321-4321-8765-2109-876543210987")
        assert result is False

    def test_semantic_search(self):
        """Test semantic search functionality"""
        service = EmbeddingsService()
        
        # Mock project access
        service.project_service = Mock()
        service.project_service.check_project_ownership.return_value = True
        
        # Mock query embedding
        service.generate_embedding = Mock(return_value=[0.5, 0.5, 0.5])
        
        # Mock stored embeddings
        stored_embeddings = [
            {
                "type": "dataset_overview",
                "text": "Sales dataset with customer data",
                "embedding": [0.5, 0.5, 0.5]  # Same as query = highest similarity (1.0)
            },
            {
                "type": "column",
                "column_name": "customer_id",
                "text": "Customer ID column",
                "embedding": [0.1, 0.1, 0.1]  # Lower similarity
            }
        ]
        service._get_project_embeddings = Mock(return_value=stored_embeddings)
        
        results = service.semantic_search("12345678-1234-5678-9012-123456789012", "87654321-4321-8765-2109-876543210987", "sales data", top_k=2)
        
        assert len(results) == 2
        assert results[0]["type"] == "dataset_overview"  # Higher similarity first
        assert results[0]["similarity"] > results[1]["similarity"]
        assert "text" in results[0]
        assert "metadata" in results[0]

    def test_semantic_search_no_access(self):
        """Test semantic search without project access"""
        service = EmbeddingsService()
        
        service.project_service = Mock()
        service.project_service.check_project_ownership.return_value = False
        
        results = service.semantic_search("12345678-1234-5678-9012-123456789012", "87654321-4321-8765-2109-876543210987", "test query")
        assert results == []

    def test_semantic_search_no_embeddings(self):
        """Test semantic search with no stored embeddings"""
        service = EmbeddingsService()
        
        service.project_service = Mock()
        service.project_service.check_project_ownership.return_value = True
        service.generate_embedding = Mock(return_value=[0.1, 0.2, 0.3])
        service._get_project_embeddings = Mock(return_value=[])
        
        results = service.semantic_search("12345678-1234-5678-9012-123456789012", "87654321-4321-8765-2109-876543210987", "test query")
        assert results == []

    def test_get_embedding_stats(self):
        """Test embedding statistics retrieval"""
        service = EmbeddingsService()
        
        service.project_service = Mock()
        service.project_service.check_project_ownership.return_value = True
        
        # Mock stored embeddings
        stored_embeddings = [
            {"type": "dataset_overview", "text": "overview"},
            {"type": "column", "text": "column1"},
            {"type": "column", "text": "column2"},
            {"type": "sample_data", "text": "samples"}
        ]
        service._get_project_embeddings = Mock(return_value=stored_embeddings)
        
        stats = service.get_embedding_stats("12345678-1234-5678-9012-123456789012", "87654321-4321-8765-2109-876543210987")
        
        assert stats["embedding_count"] == 4
        assert stats["types"]["column"] == 2
        assert stats["types"]["dataset_overview"] == 1
        assert stats["types"]["sample_data"] == 1
        assert stats["has_overview"] is True
        assert stats["has_columns"] is True
        assert stats["has_sample_data"] is True

    def test_get_embedding_stats_no_access(self):
        """Test embedding stats without project access"""
        service = EmbeddingsService()
        
        service.project_service = Mock()
        service.project_service.check_project_ownership.return_value = False
        
        stats = service.get_embedding_stats("12345678-1234-5678-9012-123456789012", "87654321-4321-8765-2109-876543210987")
        assert stats == {}

    def test_create_dataset_overview(self):
        """Test dataset overview text creation"""
        service = EmbeddingsService()
        
        mock_project = Mock()
        mock_project.name = "Sales Data"
        mock_project.description = "Customer sales information"
        mock_project.row_count = 1000
        mock_project.column_count = 5
        mock_project.columns_metadata = [
            {"name": "id", "type": "number"},
            {"name": "name", "type": "string"},
            {"name": "amount", "type": "number"}
        ]
        
        overview = service._create_dataset_overview(mock_project)
        
        assert "Sales Data" in overview
        assert "Customer sales information" in overview
        assert "1000 rows" in overview
        assert "5 columns" in overview
        assert "id, name, amount" in overview

    def test_create_column_description(self):
        """Test column description text creation"""
        service = EmbeddingsService()
        
        col_metadata = {
            "name": "customer_id",
            "type": "number",
            "sample_values": [1, 2, 3, 4, 5],
            "nullable": True
        }
        
        description = service._create_column_description(col_metadata)
        
        assert "customer_id" in description
        assert "number" in description
        assert "1, 2, 3" in description
        assert "null values" in description

    def test_create_sample_data_description(self):
        """Test sample data description creation"""
        service = EmbeddingsService()
        
        mock_project = Mock()
        mock_project.columns_metadata = [
            {
                "name": "price",
                "sample_values": [10.5, 20.0, 15.75]
            },
            {
                "name": "category",
                "sample_values": ["A", "B", "A", "C"]
            }
        ]
        
        description = service._create_sample_data_description(mock_project)
        
        assert "price ranges from 10.5 to 20.0" in description
        assert "category includes" in description

    def test_embedding_storage_and_retrieval(self):
        """Test embedding storage and retrieval"""
        service = EmbeddingsService()
        
        test_embeddings = [
            {"type": "test", "text": "test text", "embedding": [0.1, 0.2, 0.3]}
        ]
        
        # Store embeddings
        project_id = "12345678-1234-5678-9012-123456789012"
        service._store_project_embeddings(project_id, test_embeddings)
        
        # Retrieve embeddings
        retrieved = service._get_project_embeddings(project_id)
        
        assert retrieved == test_embeddings
        
        # Test non-existent project
        empty = service._get_project_embeddings("nonexistent")
        assert empty == []


def test_embeddings_service_singleton():
    """Test that embeddings_service singleton is properly initialized"""
    # This should not raise an error in testing environment
    with patch.dict("os.environ", {"TESTING": "true"}, clear=True):
        service = get_embeddings_service()
        assert service is not None
        assert isinstance(service, EmbeddingsService)
        
        # Test that it returns the same instance
        service2 = get_embeddings_service()
        assert service is service2