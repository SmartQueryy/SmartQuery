import logging
import os
import uuid
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity

from services.database_service import get_db_service
from services.project_service import get_project_service

logger = logging.getLogger(__name__)


class EmbeddingsService:
    """Service for generating and managing OpenAI embeddings for semantic search"""

    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

        # Don't require API key during testing
        if not self.openai_api_key and not os.getenv("TESTING"):
            raise ValueError("OPENAI_API_KEY environment variable not set")

        # Set embedding model regardless of client availability
        self.embedding_model = (
            "text-embedding-3-small"  # Cost-effective, good performance
        )

        # Initialize OpenAI client if API key is available
        if self.openai_api_key:
            try:
                self.client = OpenAI(api_key=self.openai_api_key)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                self.client = None
        else:
            self.client = None

        # Initialize services only if not in testing mode
        if not os.getenv("TESTING"):
            self.db_service = get_db_service()
            self.project_service = get_project_service()
        else:
            self.db_service = None
            self.project_service = None

        # In-memory storage for development/testing
        # In production, this would be replaced with vector database (Pinecone, Weaviate, etc.)
        self._embeddings_store: Dict[str, Dict[str, Any]] = {}

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for given text using OpenAI"""
        try:
            if not self.client:
                logger.warning("OpenAI client not available, returning None embedding")
                return None

            # Clean and prepare text
            cleaned_text = text.strip()
            if not cleaned_text:
                return None

            # Generate embedding
            response = self.client.embeddings.create(
                model=self.embedding_model, input=cleaned_text
            )

            embedding = response.data[0].embedding
            logger.info(f"Generated embedding for text (length: {len(cleaned_text)})")
            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            return None

    def generate_project_embeddings(self, project_id: str, user_id: str) -> bool:
        """Generate embeddings for a project's schema and sample data"""
        try:
            # Validate project access
            project_uuid = uuid.UUID(project_id)
            user_uuid = uuid.UUID(user_id)

            if (
                self.project_service
                and not self.project_service.check_project_ownership(
                    project_uuid, user_uuid
                )
            ):
                raise ValueError("Project not found or access denied")

            # Get project data
            if self.project_service:
                project = self.project_service.get_project_by_id(project_uuid)
                if not project or not project.columns_metadata:
                    raise ValueError("Project not found or no metadata available")
            else:
                # Testing mode - use mock project data
                from unittest.mock import Mock

                project = Mock()
                project.name = "Test Dataset"
                project.description = "Test description"
                project.row_count = 100
                project.column_count = 3
                project.columns_metadata = [
                    {"name": "id", "type": "number", "sample_values": [1, 2, 3]},
                    {
                        "name": "name",
                        "type": "string",
                        "sample_values": ["A", "B", "C"],
                    },
                ]

            # Generate embeddings for different aspects of the data
            embeddings_data = []

            # 1. Dataset overview embedding
            overview_text = self._create_dataset_overview(project)
            overview_embedding = self.generate_embedding(overview_text)
            if overview_embedding:
                embeddings_data.append(
                    {
                        "type": "dataset_overview",
                        "text": overview_text,
                        "embedding": overview_embedding,
                    }
                )

            # 2. Column-specific embeddings
            for col_metadata in project.columns_metadata:
                col_text = self._create_column_description(col_metadata)
                col_embedding = self.generate_embedding(col_text)
                if col_embedding:
                    embeddings_data.append(
                        {
                            "type": "column",
                            "column_name": col_metadata.get("name", ""),
                            "text": col_text,
                            "embedding": col_embedding,
                        }
                    )

            # 3. Sample data patterns embedding
            sample_text = self._create_sample_data_description(project)
            sample_embedding = self.generate_embedding(sample_text)
            if sample_embedding:
                embeddings_data.append(
                    {
                        "type": "sample_data",
                        "text": sample_text,
                        "embedding": sample_embedding,
                    }
                )

            # Store embeddings
            self._store_project_embeddings(project_id, embeddings_data)

            logger.info(
                f"Generated {len(embeddings_data)} embeddings for project {project_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Error generating project embeddings: {str(e)}")
            return False

    def semantic_search(
        self, project_id: str, user_id: str, query: str, top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Perform semantic search on project embeddings"""
        try:
            # Validate project access
            project_uuid = uuid.UUID(project_id)
            user_uuid = uuid.UUID(user_id)

            if (
                self.project_service
                and not self.project_service.check_project_ownership(
                    project_uuid, user_uuid
                )
            ):
                return []

            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            if not query_embedding:
                return []

            # Get stored embeddings for project
            project_embeddings = self._get_project_embeddings(project_id)
            if not project_embeddings:
                logger.warning(f"No embeddings found for project {project_id}")
                return []

            # Calculate similarities
            similarities = []
            query_vec = np.array(query_embedding).reshape(1, -1)

            for embedding_data in project_embeddings:
                stored_embedding = embedding_data.get("embedding")
                if stored_embedding:
                    stored_vec = np.array(stored_embedding).reshape(1, -1)
                    similarity = cosine_similarity(query_vec, stored_vec)[0][0]

                    similarities.append(
                        {
                            "similarity": float(similarity),
                            "type": embedding_data.get("type"),
                            "text": embedding_data.get("text"),
                            "column_name": embedding_data.get("column_name"),
                            "metadata": {
                                k: v
                                for k, v in embedding_data.items()
                                if k not in ["embedding", "text"]
                            },
                        }
                    )

            # Sort by similarity and return top_k results
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            results = similarities[:top_k]

            logger.info(
                f"Semantic search returned {len(results)} results for query: {query[:50]}..."
            )
            return results

        except Exception as e:
            logger.error(f"Error in semantic search: {str(e)}")
            return []

    def get_embedding_stats(self, project_id: str, user_id: str) -> Dict[str, Any]:
        """Get statistics about embeddings for a project"""
        try:
            # Validate project access
            project_uuid = uuid.UUID(project_id)
            user_uuid = uuid.UUID(user_id)

            if (
                self.project_service
                and not self.project_service.check_project_ownership(
                    project_uuid, user_uuid
                )
            ):
                return {}

            project_embeddings = self._get_project_embeddings(project_id)
            if not project_embeddings:
                return {"embedding_count": 0, "types": []}

            # Calculate statistics
            embedding_types = {}
            for embedding in project_embeddings:
                embed_type = embedding.get("type", "unknown")
                embedding_types[embed_type] = embedding_types.get(embed_type, 0) + 1

            return {
                "embedding_count": len(project_embeddings),
                "types": embedding_types,
                "has_overview": any(
                    e.get("type") == "dataset_overview" for e in project_embeddings
                ),
                "has_columns": any(
                    e.get("type") == "column" for e in project_embeddings
                ),
                "has_sample_data": any(
                    e.get("type") == "sample_data" for e in project_embeddings
                ),
            }

        except Exception as e:
            logger.error(f"Error getting embedding stats: {str(e)}")
            return {}

    def _create_dataset_overview(self, project) -> str:
        """Create a descriptive overview of the dataset for embedding"""
        try:
            overview_parts = []

            # Basic dataset info
            overview_parts.append(f"Dataset: {project.name}")
            if project.description:
                overview_parts.append(f"Description: {project.description}")

            # Size information
            if project.row_count:
                overview_parts.append(f"Contains {project.row_count} rows")
            if project.column_count:
                overview_parts.append(f"Has {project.column_count} columns")

            # Column information
            if project.columns_metadata:
                column_names = [col.get("name", "") for col in project.columns_metadata]
                overview_parts.append(f"Columns: {', '.join(column_names)}")

                # Data types
                data_types = {}
                for col in project.columns_metadata:
                    col_type = col.get("type", "unknown")
                    data_types[col_type] = data_types.get(col_type, 0) + 1

                type_desc = ", ".join(
                    [f"{count} {dtype}" for dtype, count in data_types.items()]
                )
                overview_parts.append(f"Data types: {type_desc}")

            return " | ".join(overview_parts)

        except Exception as e:
            logger.error(f"Error creating dataset overview: {str(e)}")
            return f"Dataset: {getattr(project, 'name', 'Unknown')}"

    def _create_column_description(self, col_metadata: Dict[str, Any]) -> str:
        """Create a descriptive text for a column for embedding"""
        try:
            parts = []

            col_name = col_metadata.get("name", "")
            col_type = col_metadata.get("type", "unknown")

            parts.append(f"Column {col_name} of type {col_type}")

            # Add sample values if available
            sample_values = col_metadata.get("sample_values", [])
            if sample_values:
                sample_str = ", ".join(str(v) for v in sample_values[:3])
                parts.append(f"Sample values: {sample_str}")

            # Add any additional metadata
            if col_metadata.get("nullable"):
                parts.append("allows null values")

            return " | ".join(parts)

        except Exception as e:
            logger.error(f"Error creating column description: {str(e)}")
            return f"Column {col_metadata.get('name', 'unknown')}"

    def _create_sample_data_description(self, project) -> str:
        """Create a description of sample data patterns for embedding"""
        try:
            if not project.columns_metadata:
                return "No sample data available"

            descriptions = []

            for col in project.columns_metadata:
                col_name = col.get("name", "")
                sample_values = col.get("sample_values", [])

                if sample_values and col_name:
                    # Analyze sample values to describe patterns
                    if all(isinstance(v, (int, float)) for v in sample_values):
                        min_val = min(sample_values)
                        max_val = max(sample_values)
                        descriptions.append(
                            f"{col_name} ranges from {min_val} to {max_val}"
                        )
                    else:
                        unique_vals = list(set(str(v) for v in sample_values))[:3]
                        descriptions.append(
                            f"{col_name} includes {', '.join(unique_vals)}"
                        )

            return (
                " | ".join(descriptions)
                if descriptions
                else "Sample data patterns not available"
            )

        except Exception as e:
            logger.error(f"Error creating sample data description: {str(e)}")
            return "Sample data patterns not available"

    def _store_project_embeddings(
        self, project_id: str, embeddings_data: List[Dict[str, Any]]
    ):
        """Store embeddings in memory (would be database in production)"""
        self._embeddings_store[project_id] = embeddings_data

    def _get_project_embeddings(self, project_id: str) -> List[Dict[str, Any]]:
        """Retrieve embeddings from memory (would be database in production)"""
        return self._embeddings_store.get(project_id, [])


# Singleton instance - lazy initialization
_embeddings_service_instance = None


def get_embeddings_service():
    """Get embeddings service singleton instance"""
    global _embeddings_service_instance
    if _embeddings_service_instance is None:
        _embeddings_service_instance = EmbeddingsService()
    return _embeddings_service_instance


# For backward compatibility
embeddings_service = None
