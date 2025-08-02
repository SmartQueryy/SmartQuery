import uuid
from unittest.mock import Mock, patch
import pytest

from services.suggestions_service import SuggestionsService, get_suggestions_service


class TestSuggestionsService:
    """Test suggestions service functionality"""

    def test_suggestions_service_initialization(self):
        """Test suggestions service initialization"""
        with patch.dict("os.environ", {"TESTING": "true"}, clear=True):
            service = SuggestionsService()
            assert service.project_service is None
            assert service.embeddings_service is None

    def test_suggestions_service_production_mode(self):
        """Test suggestions service initialization in production mode"""
        with patch.dict("os.environ", {}, clear=True):
            with (
                patch(
                    "services.suggestions_service.get_project_service"
                ) as mock_project,
                patch(
                    "services.suggestions_service.get_embeddings_service"
                ) as mock_embeddings,
            ):
                service = SuggestionsService()
                mock_project.assert_called_once()
                mock_embeddings.assert_called_once()

    def test_generate_suggestions_with_mock_data(self):
        """Test suggestions generation with mock project data"""
        with patch.dict("os.environ", {"TESTING": "true"}, clear=True):
            service = SuggestionsService()

            project_id = "12345678-1234-5678-9012-123456789012"
            user_id = "87654321-4321-8765-2109-876543210987"

            suggestions = service.generate_suggestions(project_id, user_id)

            assert len(suggestions) > 0
            assert len(suggestions) <= 5  # Should limit to max_suggestions

            # Check structure of suggestions
            for suggestion in suggestions:
                assert "id" in suggestion
                assert "text" in suggestion
                assert "category" in suggestion
                assert "complexity" in suggestion
                assert "confidence" in suggestion

    def test_generate_suggestions_with_real_project_data(self):
        """Test suggestions generation with real project data"""
        service = SuggestionsService()

        # Mock project and services
        mock_project = Mock()
        mock_project.name = "Sales Dataset"
        mock_project.description = "Customer sales data"
        mock_project.row_count = 1000
        mock_project.column_count = 4
        mock_project.columns_metadata = [
            {"name": "customer_id", "type": "number", "sample_values": [1, 2, 3]},
            {
                "name": "product_name",
                "type": "string",
                "sample_values": ["Product A", "Product B"],
            },
            {"name": "sales_amount", "type": "number", "sample_values": [100.0, 250.0]},
            {
                "name": "order_date",
                "type": "date",
                "sample_values": ["2024-01-01", "2024-01-02"],
            },
        ]

        service.project_service = Mock()
        service.project_service.check_project_ownership.return_value = True
        service.project_service.get_project_by_id.return_value = mock_project

        service.embeddings_service = Mock()
        service.embeddings_service.get_embedding_stats.return_value = {
            "embedding_count": 0
        }
        service.embeddings_service.generate_project_embeddings.return_value = True
        service.embeddings_service.semantic_search.return_value = []

        project_id = "12345678-1234-5678-9012-123456789012"
        user_id = "87654321-4321-8765-2109-876543210987"

        suggestions = service.generate_suggestions(
            project_id, user_id, max_suggestions=10
        )

        assert len(suggestions) > 0

        # Should have numeric aggregation suggestions
        numeric_suggestions = [
            s for s in suggestions if "total" in s["text"] or "average" in s["text"]
        ]
        assert len(numeric_suggestions) > 0

        # Should have breakdown suggestions (check for various breakdown patterns)
        breakdown_suggestions = [
            s
            for s in suggestions
            if "break down" in s["text"].lower()
            or "breakdown" in s["text"].lower()
            or s.get("type") == "breakdown"
        ]
        assert len(breakdown_suggestions) > 0

    def test_generate_suggestions_no_access(self):
        """Test suggestions generation without project access"""
        service = SuggestionsService()

        service.project_service = Mock()
        service.project_service.check_project_ownership.return_value = False

        project_id = "12345678-1234-5678-9012-123456789012"
        user_id = "87654321-4321-8765-2109-876543210987"

        suggestions = service.generate_suggestions(project_id, user_id)

        # Should return fallback suggestions
        assert len(suggestions) > 0
        fallback_ids = [s["id"] for s in suggestions]
        assert any("fallback" in id for id in fallback_ids)

    def test_generate_schema_based_suggestions(self):
        """Test schema-based suggestion generation"""
        service = SuggestionsService()

        # Mock project with diverse column types
        mock_project = Mock()
        mock_project.columns_metadata = [
            {"name": "sales_amount", "type": "number"},
            {"name": "quantity", "type": "integer"},
            {"name": "category", "type": "string"},
            {"name": "region", "type": "text"},
            {"name": "order_date", "type": "date"},
            {"name": "created_at", "type": "datetime"},
        ]

        suggestions = service._generate_schema_based_suggestions(mock_project)

        assert len(suggestions) > 0

        # Check for different types of suggestions
        suggestion_types = {s.get("type") for s in suggestions}
        assert "aggregation" in suggestion_types
        assert "breakdown" in suggestion_types
        assert "visualization" in suggestion_types
        assert "time_series" in suggestion_types

    def test_generate_embedding_based_suggestions(self):
        """Test embedding-based suggestion generation"""
        service = SuggestionsService()

        # Mock embeddings service
        mock_embeddings = Mock()
        mock_embeddings.get_embedding_stats.return_value = {"embedding_count": 5}
        mock_embeddings.semantic_search.return_value = [
            {
                "similarity": 0.8,
                "type": "dataset_overview",
                "text": "Sales dataset overview",
                "metadata": {},
            }
        ]
        service.embeddings_service = mock_embeddings

        mock_project = Mock()
        project_id = "12345678-1234-5678-9012-123456789012"
        user_id = "87654321-4321-8765-2109-876543210987"

        suggestions = service._generate_embedding_based_suggestions(
            project_id, user_id, mock_project
        )

        assert len(suggestions) > 0

        # Should have semantic suggestions
        semantic_suggestions = [
            s for s in suggestions if s.get("type") == "semantic_analysis"
        ]
        assert len(semantic_suggestions) > 0

        # Should have confidence scores
        for suggestion in suggestions:
            assert "confidence" in suggestion
            assert 0 <= suggestion["confidence"] <= 1

    def test_generate_general_suggestions(self):
        """Test general suggestion generation"""
        service = SuggestionsService()

        mock_project = Mock()
        mock_project.name = "Customer_Data"

        suggestions = service._generate_general_suggestions(mock_project)

        assert len(suggestions) > 0

        # Should include overview suggestion
        overview_suggestions = [
            s for s in suggestions if "overview" in s["text"].lower()
        ]
        assert len(overview_suggestions) > 0

        # Should include sample data suggestion
        sample_suggestions = [s for s in suggestions if "sample" in s["text"].lower()]
        assert len(sample_suggestions) > 0

    def test_deduplicate_suggestions(self):
        """Test suggestion deduplication"""
        service = SuggestionsService()

        suggestions = [
            {"id": "1", "text": "Show total sales", "confidence": 0.9},
            {"id": "2", "text": "Show total sales", "confidence": 0.8},  # Duplicate
            {"id": "3", "text": "Show average sales", "confidence": 0.7},
            {
                "id": "4",
                "text": "Show Total Sales",
                "confidence": 0.6,
            },  # Case-insensitive duplicate
        ]

        unique = service._deduplicate_suggestions(suggestions)

        assert len(unique) == 2  # Should remove duplicates
        assert unique[0]["confidence"] == 0.9  # Should sort by confidence
        assert unique[1]["text"] == "Show average sales"

    def test_get_fallback_suggestions(self):
        """Test fallback suggestion generation"""
        service = SuggestionsService()

        suggestions = service._get_fallback_suggestions()

        assert len(suggestions) > 0

        # All should be fallback suggestions
        for suggestion in suggestions:
            assert "fallback" in suggestion["id"]
            assert "confidence" in suggestion
            assert (
                suggestion["confidence"] <= 0.7
            )  # Fallback suggestions have lower confidence

    def test_generate_suggestions_with_embeddings_integration(self):
        """Test full suggestions generation with embeddings integration"""
        service = SuggestionsService()

        # Mock project
        mock_project = Mock()
        mock_project.name = "Sales Dataset"
        mock_project.columns_metadata = [
            {"name": "revenue", "type": "number"},
            {"name": "category", "type": "string"},
        ]

        # Mock services
        service.project_service = Mock()
        service.project_service.check_project_ownership.return_value = True
        service.project_service.get_project_by_id.return_value = mock_project

        service.embeddings_service = Mock()
        service.embeddings_service.get_embedding_stats.return_value = {
            "embedding_count": 3
        }
        service.embeddings_service.semantic_search.return_value = [
            {
                "similarity": 0.85,
                "type": "column",
                "column_name": "revenue",
                "text": "Revenue column analysis",
                "metadata": {},
            }
        ]

        project_id = "12345678-1234-5678-9012-123456789012"
        user_id = "87654321-4321-8765-2109-876543210987"

        suggestions = service.generate_suggestions(
            project_id, user_id, max_suggestions=10
        )

        assert len(suggestions) > 0
        assert len(suggestions) <= 10

        # Should have mix of suggestion types
        suggestion_types = {s.get("type") for s in suggestions}
        assert len(suggestion_types) > 1  # Multiple types of suggestions

    def test_invalid_project_id(self):
        """Test suggestions generation with invalid project ID"""
        service = SuggestionsService()

        # Should return fallback suggestions instead of raising error
        suggestions = service.generate_suggestions(
            "invalid-uuid", "87654321-4321-8765-2109-876543210987"
        )

        # Should return fallback suggestions
        assert len(suggestions) > 0
        fallback_ids = [s["id"] for s in suggestions]
        assert any("fallback" in id for id in fallback_ids)

    def test_suggestions_service_singleton(self):
        """Test that suggestions service singleton works correctly"""
        with patch.dict("os.environ", {"TESTING": "true"}, clear=True):
            service1 = get_suggestions_service()
            service2 = get_suggestions_service()

            assert service1 is service2  # Should be the same instance
            assert isinstance(service1, SuggestionsService)


def test_suggestions_service_module_level():
    """Test module-level functionality"""
    # Test that get_suggestions_service works
    with patch.dict("os.environ", {"TESTING": "true"}, clear=True):
        service = get_suggestions_service()
        assert service is not None
        assert isinstance(service, SuggestionsService)
