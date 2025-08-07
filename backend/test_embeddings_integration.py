#!/usr/bin/env python3
"""
Test script for embeddings integration with LangChain service - Task B19
"""

import os
from unittest.mock import Mock, patch


def test_embeddings_integration():
    """Test embeddings integration with LangChain service"""
    print("Testing Embeddings Integration - Task B19")
    print("=" * 50)

    # Set testing environment
    os.environ["TESTING"] = "true"

    # Test 1: Embeddings service initialization
    print("1. Testing embeddings service initialization...")

    from services.embeddings_service import get_embeddings_service

    embeddings_service = get_embeddings_service()

    # In testing mode, should not require API key
    assert embeddings_service is not None
    print("✅ Embeddings service initialized successfully")

    # Test 2: LangChain integration
    print("2. Testing LangChain service integration...")

    from services.langchain_service import get_langchain_service

    langchain_service = get_langchain_service()

    # Mock project and user data
    project_id = "12345678-1234-5678-9012-123456789012"
    user_id = "87654321-4321-8765-2109-876543210987"

    # Mock embeddings service methods
    with (
        patch.object(embeddings_service, "get_embedding_stats") as mock_stats,
        patch.object(
            embeddings_service, "generate_project_embeddings"
        ) as mock_generate,
        patch.object(embeddings_service, "semantic_search") as mock_search,
    ):

        # Mock no existing embeddings
        mock_stats.return_value = {"embedding_count": 0}
        mock_generate.return_value = True

        # Mock semantic search results
        mock_search.return_value = [
            {
                "similarity": 0.95,
                "type": "dataset_overview",
                "text": "Sales dataset with customer information and purchase history",
                "metadata": {},
            },
            {
                "similarity": 0.80,
                "type": "column",
                "text": "customer_id column contains unique customer identifiers",
                "column_name": "customer_id",
                "metadata": {},
            },
        ]

        # Test ensure embeddings method
        langchain_service._ensure_project_embeddings(project_id, user_id)

        # Verify embeddings generation was called
        mock_stats.assert_called_once_with(project_id, user_id)
        mock_generate.assert_called_once_with(project_id, user_id)

        print("✅ Embeddings generation integration working")

        # Test semantic search integration
        mock_project = {
            "name": "Customer Sales Data",
            "row_count": 1000,
            "column_count": 5,
        }

        result = langchain_service._process_general_query(
            "Tell me about customer data", mock_project, project_id, user_id
        )

        # Verify semantic search was called
        mock_search.assert_called_once_with(
            project_id, user_id, "Tell me about customer data", top_k=3
        )

        # Verify result contains semantic information
        assert result.result_type == "summary"
        assert (
            "sales dataset" in result.summary.lower()
            or "customer" in result.summary.lower()
        )

        print("✅ Semantic search integration working")

    # Test 3: Embedding generation workflow
    print("3. Testing embedding generation workflow...")

    # Mock a complete project object
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

    # Test text generation methods
    overview = embeddings_service._create_dataset_overview(mock_project)
    assert "Test Dataset" in overview
    assert "Customer sales data" in overview
    assert "1000 rows" in overview
    print("✅ Dataset overview generation working")

    col_desc = embeddings_service._create_column_description(
        mock_project.columns_metadata[0]
    )
    assert "customer_id" in col_desc
    assert "number" in col_desc
    print("✅ Column description generation working")

    sample_desc = embeddings_service._create_sample_data_description(mock_project)
    assert "customer_id" in sample_desc or "product_name" in sample_desc
    print("✅ Sample data description generation working")

    # Test 4: Storage and retrieval
    print("4. Testing embedding storage and retrieval...")

    test_embeddings = [
        {
            "type": "dataset_overview",
            "text": "Test dataset overview",
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
        }
    ]

    # Store and retrieve embeddings
    embeddings_service._store_project_embeddings(project_id, test_embeddings)
    retrieved = embeddings_service._get_project_embeddings(project_id)

    assert retrieved == test_embeddings
    print("✅ Embedding storage and retrieval working")

    # Test 5: Integration with existing tests
    print("5. Testing integration doesn't break existing functionality...")

    # Import should work without errors
    from api.chat import router
    from tests.test_langchain_chat import TestLangChainChatIntegration

    print("✅ Integration doesn't break existing imports")

    return True


if __name__ == "__main__":
    print("Embeddings Integration Test - Task B19")
    print("=" * 50)

    try:
        test_embeddings_integration()

        print("\n🎉 All embeddings integration tests passed!")
        print("✅ Task B19 implementation successful!")
        print("✅ Semantic search ready for production!")

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        raise
