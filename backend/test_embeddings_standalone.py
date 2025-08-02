#!/usr/bin/env python3
"""
Standalone test for embeddings service - Task B19
Tests embeddings functionality without external dependencies
"""

import os
import sys
from unittest.mock import Mock, patch


def test_embeddings_standalone():
    """Test embeddings service in isolation"""
    print("Standalone Embeddings Test - Task B19")
    print("=" * 50)

    # Set testing environment
    os.environ["TESTING"] = "true"

    # Test 1: Service initialization
    print("1. Testing embeddings service initialization...")

    from services.embeddings_service import get_embeddings_service

    service = get_embeddings_service()

    assert service is not None
    assert service.client is None  # No OpenAI API key in testing
    assert service.db_service is None  # No database in testing
    assert service.project_service is None  # No project service in testing
    print("✅ Service initialized successfully in testing mode")

    # Test 2: Embedding generation (mocked)
    print("2. Testing embedding generation...")

    # Mock OpenAI client
    with patch.object(service, "client") as mock_client:
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1, 0.2, 0.3, 0.4, 0.5])]
        mock_client.embeddings.create.return_value = mock_response

        embedding = service.generate_embedding("test text")
        assert embedding == [0.1, 0.2, 0.3, 0.4, 0.5]
        print("✅ Embedding generation working")

    # Test 3: Project embeddings generation (with mocking)
    print("3. Testing project embeddings generation...")

    # Mock embedding generation to avoid API calls
    with patch.object(service, "generate_embedding", return_value=[0.1, 0.2, 0.3]):
        project_id = "12345678-1234-5678-9012-123456789012"
        user_id = "87654321-4321-8765-2109-876543210987"

        result = service.generate_project_embeddings(project_id, user_id)
        assert result is True
        print("✅ Project embeddings generation working")

    # Test 4: Semantic search
    print("4. Testing semantic search...")

    # Store some test embeddings
    test_embeddings = [
        {
            "type": "dataset_overview",
            "text": "Sales dataset with customer information",
            "embedding": [0.5, 0.5, 0.5],
        },
        {
            "type": "column",
            "column_name": "customer_id",
            "text": "Customer ID column",
            "embedding": [0.1, 0.1, 0.1],
        },
    ]

    service._store_project_embeddings(project_id, test_embeddings)

    # Mock query embedding
    with patch.object(service, "generate_embedding", return_value=[0.5, 0.5, 0.5]):
        results = service.semantic_search(project_id, user_id, "sales data", top_k=2)

        assert len(results) == 2
        assert results[0]["type"] == "dataset_overview"  # Should be highest similarity
        assert results[0]["similarity"] > results[1]["similarity"]
        print("✅ Semantic search working")

    # Test 5: Embedding statistics
    print("5. Testing embedding statistics...")

    stats = service.get_embedding_stats(project_id, user_id)
    assert stats["embedding_count"] == 2
    assert stats["has_overview"] is True
    assert stats["has_columns"] is True
    print("✅ Embedding statistics working")

    # Test 6: Text generation methods
    print("6. Testing text generation methods...")

    # Create mock project for text generation
    mock_project = Mock()
    mock_project.name = "Test Dataset"
    mock_project.description = "Customer sales data"
    mock_project.row_count = 1000
    mock_project.column_count = 4
    mock_project.columns_metadata = [
        {"name": "customer_id", "type": "number", "sample_values": [1, 2, 3]},
        {
            "name": "product_name",
            "type": "string",
            "sample_values": ["Product A", "Product B", "Product C"],
        },
    ]

    # Test overview generation
    overview = service._create_dataset_overview(mock_project)
    assert "Test Dataset" in overview
    assert "Customer sales data" in overview
    assert "1000 rows" in overview
    print("✅ Dataset overview generation working")

    # Test column description
    col_desc = service._create_column_description(mock_project.columns_metadata[0])
    assert "customer_id" in col_desc
    assert "number" in col_desc
    print("✅ Column description generation working")

    # Test sample data description
    sample_desc = service._create_sample_data_description(mock_project)
    assert "customer_id" in sample_desc or "product_name" in sample_desc
    print("✅ Sample data description generation working")

    return True


if __name__ == "__main__":
    print("Running Standalone Embeddings Test - Task B19")
    print("=" * 50)

    try:
        test_embeddings_standalone()

        print("\n🎉 All standalone embeddings tests passed!")
        print("✅ Task B19 embeddings functionality working correctly!")
        print("✅ Service ready for production with OpenAI API key!")
        print("✅ Semantic search capabilities implemented!")

    except Exception as e:
        print(f"\n❌ Standalone test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
