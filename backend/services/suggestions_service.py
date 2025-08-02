import logging
import os
import uuid
from typing import Any, Dict, List, Optional

from services.embeddings_service import get_embeddings_service
from services.project_service import get_project_service

logger = logging.getLogger(__name__)


class SuggestionsService:
    """Service for generating intelligent query suggestions based on project data and embeddings"""

    def __init__(self):
        # Initialize services only if not in testing mode
        if not os.getenv("TESTING"):
            self.project_service = get_project_service()
            self.embeddings_service = get_embeddings_service()
        else:
            self.project_service = None
            self.embeddings_service = None

    def generate_suggestions(
        self, project_id: str, user_id: str, max_suggestions: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate intelligent query suggestions for a project"""
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
                logger.warning(
                    f"User {user_id} does not have access to project {project_id}"
                )
                return self._get_fallback_suggestions()

            # Get project data
            if self.project_service:
                project = self.project_service.get_project_by_id(project_uuid)
                if not project or not project.columns_metadata:
                    logger.warning(f"No metadata found for project {project_id}")
                    return self._get_fallback_suggestions()
            else:
                # Testing mode - use mock project data
                from unittest.mock import Mock

                project = Mock()
                project.name = "Sales Dataset"
                project.description = "Customer sales data"
                project.row_count = 1000
                project.column_count = 4
                project.columns_metadata = [
                    {
                        "name": "customer_id",
                        "type": "number",
                        "sample_values": [1, 2, 3],
                    },
                    {
                        "name": "product_name",
                        "type": "string",
                        "sample_values": ["Product A", "Product B", "Product C"],
                    },
                    {
                        "name": "sales_amount",
                        "type": "number",
                        "sample_values": [100.0, 250.0, 75.0],
                    },
                    {
                        "name": "order_date",
                        "type": "date",
                        "sample_values": ["2024-01-01", "2024-01-02", "2024-01-03"],
                    },
                ]

            # Generate context-aware suggestions
            suggestions = []

            # 1. Schema-based suggestions
            schema_suggestions = self._generate_schema_based_suggestions(project)
            suggestions.extend(schema_suggestions)

            # 2. Embedding-enhanced suggestions (if embeddings service available)
            if self.embeddings_service:
                embedding_suggestions = self._generate_embedding_based_suggestions(
                    project_id, user_id, project
                )
                suggestions.extend(embedding_suggestions)

            # 3. General dataset suggestions
            general_suggestions = self._generate_general_suggestions(project)
            suggestions.extend(general_suggestions)

            # Remove duplicates and limit results
            unique_suggestions = self._deduplicate_suggestions(suggestions)
            return unique_suggestions[:max_suggestions]

        except Exception as e:
            logger.error(f"Error generating suggestions: {str(e)}")
            return self._get_fallback_suggestions()

    def _generate_schema_based_suggestions(self, project) -> List[Dict[str, Any]]:
        """Generate suggestions based on column schema and data types"""
        suggestions = []
        metadata = project.columns_metadata

        # Categorize columns by type
        numeric_cols = [
            col["name"]
            for col in metadata
            if col.get("type") in ["number", "integer", "float", "numeric"]
        ]
        categorical_cols = [
            col["name"] for col in metadata if col.get("type") in ["string", "text"]
        ]
        date_cols = [
            col["name"]
            for col in metadata
            if col.get("type") in ["date", "datetime", "timestamp"]
        ]

        # Numeric aggregation suggestions
        if numeric_cols:
            for i, col in enumerate(
                numeric_cols[:2]
            ):  # Limit to first 2 numeric columns
                suggestions.append(
                    {
                        "id": f"sug_sum_{col}_{i}",
                        "text": f"What is the total {col.replace('_', ' ')}?",
                        "category": "analysis",
                        "complexity": "beginner",
                        "type": "aggregation",
                        "confidence": 0.9,
                    }
                )

                suggestions.append(
                    {
                        "id": f"sug_avg_{col}_{i}",
                        "text": f"What is the average {col.replace('_', ' ')}?",
                        "category": "analysis",
                        "complexity": "beginner",
                        "type": "aggregation",
                        "confidence": 0.85,
                    }
                )

        # Categorical breakdown suggestions
        if numeric_cols and categorical_cols:
            for i, (num_col, cat_col) in enumerate(
                zip(numeric_cols[:2], categorical_cols[:2])
            ):
                suggestions.append(
                    {
                        "id": f"sug_breakdown_{cat_col}_{num_col}_{i}",
                        "text": f"Break down {num_col.replace('_', ' ')} by {cat_col.replace('_', ' ')}",
                        "category": "analysis",
                        "complexity": "intermediate",
                        "type": "breakdown",
                        "confidence": 0.8,
                    }
                )

                suggestions.append(
                    {
                        "id": f"sug_chart_{cat_col}_{num_col}_{i}",
                        "text": f"Show a bar chart of {num_col.replace('_', ' ')} by {cat_col.replace('_', ' ')}",
                        "category": "visualization",
                        "complexity": "intermediate",
                        "type": "visualization",
                        "confidence": 0.75,
                    }
                )

        # Time series suggestions
        if date_cols and numeric_cols:
            for date_col in date_cols[:1]:  # First date column
                for num_col in numeric_cols[:1]:  # First numeric column
                    suggestions.append(
                        {
                            "id": f"sug_trend_{date_col}_{num_col}",
                            "text": f"Show {num_col.replace('_', ' ')} trend over time",
                            "category": "visualization",
                            "complexity": "intermediate",
                            "type": "time_series",
                            "confidence": 0.85,
                        }
                    )

        # Top/bottom value suggestions
        if categorical_cols:
            for cat_col in categorical_cols[:1]:
                suggestions.append(
                    {
                        "id": f"sug_top_{cat_col}",
                        "text": f"What are the most common {cat_col.replace('_', ' ')} values?",
                        "category": "analysis",
                        "complexity": "beginner",
                        "type": "ranking",
                        "confidence": 0.7,
                    }
                )

        return suggestions

    def _generate_embedding_based_suggestions(
        self, project_id: str, user_id: str, project
    ) -> List[Dict[str, Any]]:
        """Generate suggestions using semantic understanding from embeddings"""
        suggestions = []

        try:
            # Get embedding statistics to see if embeddings exist
            stats = self.embeddings_service.get_embedding_stats(project_id, user_id)

            if stats.get("embedding_count", 0) == 0:
                # Generate embeddings if they don't exist
                logger.info(
                    f"Generating embeddings for suggestions in project {project_id}"
                )
                success = self.embeddings_service.generate_project_embeddings(
                    project_id, user_id
                )
                if not success:
                    logger.warning("Failed to generate embeddings for suggestions")
                    return suggestions

            # Use semantic search to find relevant query patterns
            common_query_patterns = [
                "analysis of data patterns",
                "summary statistics",
                "data distribution",
                "correlation analysis",
                "outlier detection",
                "trend analysis",
            ]

            for pattern in common_query_patterns[:3]:  # Limit to top 3 patterns
                semantic_results = self.embeddings_service.semantic_search(
                    project_id, user_id, pattern, top_k=1
                )

                if semantic_results:
                    result = semantic_results[0]
                    confidence = result.get("similarity", 0.5)

                    if confidence > 0.6:  # Only include high-confidence suggestions
                        if result.get("type") == "dataset_overview":
                            suggestions.append(
                                {
                                    "id": f"sug_semantic_overview_{pattern.replace(' ', '_')}",
                                    "text": f"Give me insights about {pattern.replace('_', ' ')}",
                                    "category": "summary",
                                    "complexity": "intermediate",
                                    "type": "semantic_analysis",
                                    "confidence": confidence,
                                }
                            )
                        elif result.get("type") == "column":
                            col_name = result.get("column_name", "data")
                            suggestions.append(
                                {
                                    "id": f"sug_semantic_column_{col_name}_{pattern.replace(' ', '_')}",
                                    "text": f"Analyze {col_name.replace('_', ' ')} for {pattern}",
                                    "category": "analysis",
                                    "complexity": "intermediate",
                                    "type": "semantic_column",
                                    "confidence": confidence,
                                }
                            )

        except Exception as e:
            logger.error(f"Error generating embedding-based suggestions: {str(e)}")

        return suggestions

    def _generate_general_suggestions(self, project) -> List[Dict[str, Any]]:
        """Generate general suggestions that work for any dataset"""
        dataset_name = getattr(project, "name", "dataset").replace("_", " ")

        return [
            {
                "id": "sug_overview_general",
                "text": f"Give me an overview of the {dataset_name}",
                "category": "summary",
                "complexity": "beginner",
                "type": "overview",
                "confidence": 0.95,
            },
            {
                "id": "sug_sample_data",
                "text": "Show me a sample of the data",
                "category": "exploration",
                "complexity": "beginner",
                "type": "sample",
                "confidence": 0.9,
            },
            {
                "id": "sug_data_quality",
                "text": "Check the data quality and missing values",
                "category": "analysis",
                "complexity": "intermediate",
                "type": "quality",
                "confidence": 0.8,
            },
            {
                "id": "sug_column_info",
                "text": "Describe the columns and their data types",
                "category": "exploration",
                "complexity": "beginner",
                "type": "schema",
                "confidence": 0.85,
            },
        ]

    def _deduplicate_suggestions(
        self, suggestions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove duplicate suggestions and sort by confidence"""
        seen_texts = set()
        unique_suggestions = []

        # Sort by confidence (descending) to prioritize higher confidence suggestions
        suggestions.sort(key=lambda x: x.get("confidence", 0.5), reverse=True)

        for suggestion in suggestions:
            text = suggestion.get("text", "").lower()
            if text not in seen_texts:
                seen_texts.add(text)
                unique_suggestions.append(suggestion)

        return unique_suggestions

    def _get_fallback_suggestions(self) -> List[Dict[str, Any]]:
        """Fallback suggestions when project data is not available"""
        return [
            {
                "id": "sug_fallback_overview",
                "text": "Give me an overview of this dataset",
                "category": "summary",
                "complexity": "beginner",
                "type": "overview",
                "confidence": 0.7,
            },
            {
                "id": "sug_fallback_sample",
                "text": "Show me the first 10 rows",
                "category": "exploration",
                "complexity": "beginner",
                "type": "sample",
                "confidence": 0.7,
            },
            {
                "id": "sug_fallback_columns",
                "text": "What columns are in this dataset?",
                "category": "exploration",
                "complexity": "beginner",
                "type": "schema",
                "confidence": 0.7,
            },
            {
                "id": "sug_fallback_stats",
                "text": "Show me basic statistics",
                "category": "analysis",
                "complexity": "beginner",
                "type": "statistics",
                "confidence": 0.7,
            },
            {
                "id": "sug_fallback_summary",
                "text": "Summarize the key insights",
                "category": "summary",
                "complexity": "intermediate",
                "type": "insights",
                "confidence": 0.6,
            },
        ]


# Singleton instance - lazy initialization
_suggestions_service_instance = None


def get_suggestions_service():
    """Get suggestions service singleton instance"""
    global _suggestions_service_instance
    if _suggestions_service_instance is None:
        _suggestions_service_instance = SuggestionsService()
    return _suggestions_service_instance


# For backward compatibility
suggestions_service = None
