import logging
import os
import uuid
from io import StringIO
from typing import Any, Dict, List, Optional

import pandas as pd
from celery import current_task

from celery_app import celery_app
from services.database_service import get_db_service
from services.project_service import get_project_service
from services.storage_service import storage_service

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def process_csv_file(self, project_id: str, user_id: str):
    """
    Process uploaded CSV file for project analysis
    """
    try:
        project_uuid = uuid.UUID(project_id)
        user_uuid = uuid.UUID(user_id)

        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"current": 10, "total": 100, "status": "Starting CSV analysis..."},
        )

        logger.info(f"Processing CSV file for project {project_id}")

        # Get project service
        project_service = get_project_service()

        # Update project status to processing
        project_service.update_project_status(project_uuid, "processing")

        # Download file from MinIO
        self.update_state(
            state="PROGRESS",
            meta={"current": 20, "total": 100, "status": "Downloading file..."},
        )

        object_name = f"{user_id}/{project_id}/data.csv"
        file_content = storage_service.download_file(object_name)

        if not file_content:
            raise Exception("Failed to download file from storage")

        # Parse CSV with pandas
        self.update_state(
            state="PROGRESS",
            meta={"current": 40, "total": 100, "status": "Parsing CSV..."},
        )

        try:
            df = pd.read_csv(StringIO(file_content.decode("utf-8")))
        except Exception as e:
            raise Exception(f"Failed to parse CSV: {str(e)}")

        # Analyze schema
        self.update_state(
            state="PROGRESS",
            meta={"current": 60, "total": 100, "status": "Analyzing schema..."},
        )

        columns_metadata = []
        for column in df.columns:
            col_type = str(df[column].dtype)
            col_series = df[column]

            # Determine data type category
            if "int" in col_type or "float" in col_type:
                data_type = "number"
            elif "datetime" in col_type:
                data_type = "datetime"
            elif "bool" in col_type:
                data_type = "boolean"
            else:
                data_type = "string"

            # Check for null values
            nullable = col_series.isnull().any()
            null_count = col_series.isnull().sum()
            null_percentage = (null_count / len(col_series)) * 100

            # Get sample values (first 5 non-null values)
            sample_values = col_series.dropna().head(5).tolist()

            # Calculate statistics for numeric columns
            statistics = {}
            if data_type == "number":
                statistics = {
                    "min": float(col_series.min()) if not col_series.empty else None,
                    "max": float(col_series.max()) if not col_series.empty else None,
                    "mean": float(col_series.mean()) if not col_series.empty else None,
                    "median": (
                        float(col_series.median()) if not col_series.empty else None
                    ),
                    "std": float(col_series.std()) if not col_series.empty else None,
                }
            elif data_type == "string":
                # String statistics
                unique_count = col_series.nunique()
                most_common = col_series.mode().tolist() if not col_series.empty else []
                avg_length = col_series.str.len().mean() if not col_series.empty else 0
                statistics = {
                    "unique_count": int(unique_count),
                    "most_common_values": most_common[:3],  # Top 3 most common
                    "average_length": (
                        float(avg_length) if not pd.isna(avg_length) else 0
                    ),
                }

            # Detect potential data quality issues
            data_quality_issues = []
            if null_percentage > 50:
                data_quality_issues.append("high_null_percentage")
            if data_type == "string" and col_series.nunique() == 1:
                data_quality_issues.append("single_value_column")
            if data_type == "number" and col_series.std() == 0:
                data_quality_issues.append("no_variance")

            columns_metadata.append(
                {
                    "name": column,
                    "type": data_type,
                    "nullable": nullable,
                    "null_count": int(null_count),
                    "null_percentage": round(null_percentage, 2),
                    "sample_values": sample_values,
                    "statistics": statistics,
                    "data_quality_issues": data_quality_issues,
                }
            )

        # Calculate dataset-level insights
        dataset_insights = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "total_cells": len(df) * len(df.columns),
            "null_cells": df.isnull().sum().sum(),
            "null_percentage": round(
                (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100, 2
            ),
            "duplicate_rows": int(df.duplicated().sum()),
            "duplicate_percentage": round((df.duplicated().sum() / len(df)) * 100, 2),
            "numeric_columns": len(
                [col for col in columns_metadata if col["type"] == "number"]
            ),
            "string_columns": len(
                [col for col in columns_metadata if col["type"] == "string"]
            ),
            "datetime_columns": len(
                [col for col in columns_metadata if col["type"] == "datetime"]
            ),
            "boolean_columns": len(
                [col for col in columns_metadata if col["type"] == "boolean"]
            ),
            "columns_with_issues": len(
                [col for col in columns_metadata if col["data_quality_issues"]]
            ),
        }

        # Update project with analysis results
        self.update_state(
            state="PROGRESS",
            meta={"current": 80, "total": 100, "status": "Updating project..."},
        )

        project_service.update_project_metadata(
            project_uuid,
            row_count=len(df),
            column_count=len(df.columns),
            columns_metadata=columns_metadata,
            status="ready",
        )

        # Final update
        self.update_state(
            state="PROGRESS",
            meta={"current": 100, "total": 100, "status": "Processing complete"},
        )

        result = {
            "project_id": project_id,
            "status": "completed",
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns_metadata": columns_metadata,
            "dataset_insights": dataset_insights,
        }

        logger.info(f"Successfully processed CSV for project {project_id}")
        return result

    except Exception as exc:
        logger.error(f"Error processing CSV for project {project_id}: {str(exc)}")

        # Update project status to error
        try:
            project_service = get_project_service()
            project_service.update_project_status(project_uuid, "error")
        except:
            pass

        self.update_state(
            state="FAILURE", meta={"error": str(exc), "project_id": project_id}
        )
        raise exc


@celery_app.task(bind=True)
def analyze_csv_schema(self, file_content: bytes, filename: str = "data.csv"):
    """
    Analyze CSV schema independently - enhanced implementation for Task B13
    """
    try:
        logger.info(f"Analyzing CSV schema for file: {filename}")

        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"current": 20, "total": 100, "status": "Parsing CSV..."},
        )

        # Parse CSV with pandas
        try:
            df = pd.read_csv(StringIO(file_content.decode("utf-8")))
        except Exception as e:
            raise Exception(f"Failed to parse CSV: {str(e)}")

        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"current": 60, "total": 100, "status": "Analyzing schema..."},
        )

        # Analyze columns
        columns_metadata = []
        for column in df.columns:
            col_type = str(df[column].dtype)
            col_series = df[column]

            # Determine data type category
            if "int" in col_type or "float" in col_type:
                data_type = "number"
            elif "datetime" in col_type:
                data_type = "datetime"
            elif "bool" in col_type:
                data_type = "boolean"
            else:
                data_type = "string"

            # Check for null values
            nullable = col_series.isnull().any()
            null_count = col_series.isnull().sum()
            null_percentage = (null_count / len(col_series)) * 100

            # Get sample values (first 5 non-null values)
            sample_values = col_series.dropna().head(5).tolist()

            # Calculate statistics for numeric columns
            statistics = {}
            if data_type == "number":
                statistics = {
                    "min": float(col_series.min()) if not col_series.empty else None,
                    "max": float(col_series.max()) if not col_series.empty else None,
                    "mean": float(col_series.mean()) if not col_series.empty else None,
                    "median": (
                        float(col_series.median()) if not col_series.empty else None
                    ),
                    "std": float(col_series.std()) if not col_series.empty else None,
                }
            elif data_type == "string":
                # String statistics
                unique_count = col_series.nunique()
                most_common = col_series.mode().tolist() if not col_series.empty else []
                avg_length = col_series.str.len().mean() if not col_series.empty else 0
                statistics = {
                    "unique_count": int(unique_count),
                    "most_common_values": most_common[:3],  # Top 3 most common
                    "average_length": (
                        float(avg_length) if not pd.isna(avg_length) else 0
                    ),
                }

            # Detect potential data quality issues
            data_quality_issues = []
            if null_percentage > 50:
                data_quality_issues.append("high_null_percentage")
            if data_type == "string" and col_series.nunique() == 1:
                data_quality_issues.append("single_value_column")
            if data_type == "number" and col_series.std() == 0:
                data_quality_issues.append("no_variance")

            columns_metadata.append(
                {
                    "name": column,
                    "type": data_type,
                    "nullable": nullable,
                    "null_count": int(null_count),
                    "null_percentage": round(null_percentage, 2),
                    "sample_values": sample_values,
                    "statistics": statistics,
                    "data_quality_issues": data_quality_issues,
                }
            )

        # Calculate dataset-level insights
        dataset_insights = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "total_cells": len(df) * len(df.columns),
            "null_cells": df.isnull().sum().sum(),
            "null_percentage": round(
                (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100, 2
            ),
            "duplicate_rows": int(df.duplicated().sum()),
            "duplicate_percentage": round((df.duplicated().sum() / len(df)) * 100, 2),
            "numeric_columns": len(
                [col for col in columns_metadata if col["type"] == "number"]
            ),
            "string_columns": len(
                [col for col in columns_metadata if col["type"] == "string"]
            ),
            "datetime_columns": len(
                [col for col in columns_metadata if col["type"] == "datetime"]
            ),
            "boolean_columns": len(
                [col for col in columns_metadata if col["type"] == "boolean"]
            ),
            "columns_with_issues": len(
                [col for col in columns_metadata if col["data_quality_issues"]]
            ),
        }

        # Update task state
        self.update_state(
            state="PROGRESS",
            meta={"current": 100, "total": 100, "status": "Analysis complete"},
        )

        schema_result = {
            "filename": filename,
            "file_size_bytes": len(file_content),
            "columns": columns_metadata,
            "dataset_insights": dataset_insights,
            "analysis_timestamp": pd.Timestamp.now().isoformat(),
        }

        logger.info(f"Successfully analyzed schema for {filename}")
        return schema_result

    except Exception as exc:
        logger.error(f"Error analyzing schema for {filename}: {str(exc)}")
        raise exc
