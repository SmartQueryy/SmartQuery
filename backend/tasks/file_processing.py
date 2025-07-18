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
            nullable = df[column].isnull().any()

            # Get sample values (first 5 non-null values)
            sample_values = df[column].dropna().head(5).tolist()

            columns_metadata.append(
                {
                    "name": column,
                    "type": data_type,
                    "nullable": nullable,
                    "sample_values": sample_values,
                }
            )

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
def analyze_csv_schema(self, file_path: str):
    """
    Analyze CSV schema - placeholder implementation for Task B2
    Will be fully implemented in Task B13
    """
    try:
        logger.info(f"Analyzing CSV schema: {file_path}")

        # Simulate schema analysis
        import time

        time.sleep(1)

        # Mock schema result
        schema = {
            "columns": [
                {
                    "name": "id",
                    "type": "integer",
                    "nullable": False,
                    "sample_values": [1, 2, 3],
                },
                {
                    "name": "name",
                    "type": "string",
                    "nullable": False,
                    "sample_values": ["John", "Jane", "Bob"],
                },
                {
                    "name": "age",
                    "type": "integer",
                    "nullable": True,
                    "sample_values": [25, 30, None],
                },
            ],
            "row_count": 1000,
            "file_size": "2.5 MB",
        }

        logger.info(f"Successfully analyzed schema for {file_path}")
        return schema

    except Exception as exc:
        logger.error(f"Error analyzing schema for {file_path}: {str(exc)}")
        raise exc
