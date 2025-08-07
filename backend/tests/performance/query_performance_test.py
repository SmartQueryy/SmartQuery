"""
Query Processing Performance Tests - Task B27

Specialized performance tests for the query processing pipeline including
LangChain, OpenAI API calls, and DuckDB query execution.
"""

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Dict, List
from unittest.mock import Mock, patch

import pytest

from models.project import ProjectCreate
from models.response_schemas import QueryResult
from models.user import GoogleOAuthData
from services.langchain_service import LangChainService
from services.project_service import get_project_service
from services.user_service import get_user_service


@dataclass
class QueryPerformanceMetrics:
    """Metrics for query performance testing"""

    operation: str
    execution_time: float
    success: bool
    error_message: str = None
    memory_usage_mb: float = 0.0
    api_calls_count: int = 0


class QueryPerformanceTester:
    """Performance tester for query processing operations"""

    def __init__(self):
        self.metrics: List[QueryPerformanceMetrics] = []
        self.user_service = get_user_service()
        self.project_service = get_project_service()
        self.langchain_service = LangChainService()

    def measure_operation(
        self, operation_name: str, operation_func, *args, **kwargs
    ) -> QueryPerformanceMetrics:
        """Measure performance of a single operation"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        start_time = time.time()
        success = True
        error_message = None

        try:
            if asyncio.iscoroutinefunction(operation_func):
                result = asyncio.run(operation_func(*args, **kwargs))
            else:
                result = operation_func(*args, **kwargs)
        except Exception as e:
            success = False
            error_message = str(e)
            result = None

        end_time = time.time()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB

        metrics = QueryPerformanceMetrics(
            operation=operation_name,
            execution_time=end_time - start_time,
            success=success,
            error_message=error_message,
            memory_usage_mb=final_memory - initial_memory,
        )

        self.metrics.append(metrics)
        return metrics

    def create_test_project_with_data(self) -> tuple:
        """Create a test project with realistic metadata for performance testing"""
        # Create test user
        google_data = GoogleOAuthData(
            google_id="perf_test_user",
            email="performance@test.com",
            name="Performance Test User",
        )
        test_user, _ = self.user_service.create_or_update_from_google_oauth(google_data)

        # Create test project
        project_data = ProjectCreate(
            name="Performance Test Project", description="Large dataset for performance testing"
        )
        test_project = self.project_service.create_project(project_data, test_user.id)

        # Create realistic large dataset metadata
        columns_metadata = [
            {"name": "id", "type": "number", "nullable": False, "sample_values": [1, 2, 3, 4, 5]},
            {
                "name": "customer_name",
                "type": "string",
                "nullable": False,
                "sample_values": [
                    "John Doe",
                    "Jane Smith",
                    "Bob Johnson",
                    "Alice Brown",
                    "Charlie Wilson",
                ],
            },
            {
                "name": "email",
                "type": "string",
                "nullable": False,
                "sample_values": [
                    "john@email.com",
                    "jane@email.com",
                    "bob@email.com",
                    "alice@email.com",
                    "charlie@email.com",
                ],
            },
            {
                "name": "age",
                "type": "number",
                "nullable": False,
                "sample_values": [25, 30, 35, 28, 42],
            },
            {
                "name": "salary",
                "type": "number",
                "nullable": False,
                "sample_values": [50000, 75000, 60000, 80000, 95000],
            },
            {
                "name": "department",
                "type": "string",
                "nullable": False,
                "sample_values": ["Engineering", "Sales", "Marketing", "HR", "Finance"],
            },
            {
                "name": "hire_date",
                "type": "date",
                "nullable": False,
                "sample_values": [
                    "2020-01-15",
                    "2019-06-10",
                    "2021-03-20",
                    "2018-11-05",
                    "2022-02-28",
                ],
            },
            {
                "name": "performance_score",
                "type": "number",
                "nullable": True,
                "sample_values": [4.2, 3.8, 4.5, 4.0, 3.9],
            },
            {
                "name": "location",
                "type": "string",
                "nullable": False,
                "sample_values": ["New York", "San Francisco", "Chicago", "Austin", "Seattle"],
            },
            {
                "name": "manager_id",
                "type": "number",
                "nullable": True,
                "sample_values": [101, 102, 103, 104, 105],
            },
        ]

        # Update project with large dataset simulation (100K rows)
        self.project_service.update_project_metadata(
            test_project.id,
            row_count=100000,
            column_count=len(columns_metadata),
            columns_metadata=columns_metadata,
        )
        self.project_service.update_project_status(test_project.id, "ready")

        return test_user, test_project

    def test_langchain_query_processing_performance(self):
        """Test LangChain query processing performance with various query types"""
        test_user, test_project = self.create_test_project_with_data()

        # Define test queries of varying complexity
        test_queries = [
            ("Simple SELECT", "Show me all employees"),
            ("Filtered Query", "Show me employees with salary greater than 70000"),
            ("Aggregation Query", "What is the average salary by department?"),
            (
                "Complex Join",
                "Show me employees and their managers with performance scores above 4.0",
            ),
            ("Date Range Query", "Show me employees hired in the last 2 years"),
            ("Statistical Query", "What are the salary percentiles by department?"),
            (
                "Multi-condition Filter",
                "Show me engineers in New York with salary between 60000 and 90000",
            ),
            (
                "Grouping with Having",
                "Which departments have more than 10 employees with average salary above 70000?",
            ),
        ]

        query_performance_results = []

        with patch("services.langchain_service.ChatOpenAI") as mock_openai:
            # Mock OpenAI responses for different query types
            mock_llm = Mock()

            def mock_sql_response(messages):
                query_text = messages[0].content.lower()
                if "average" in query_text and "department" in query_text:
                    return Mock(
                        content="SELECT department, AVG(salary) as avg_salary FROM data GROUP BY department"
                    )
                elif "salary greater than" in query_text:
                    return Mock(content="SELECT * FROM data WHERE salary > 70000")
                elif "percentiles" in query_text:
                    return Mock(
                        content="SELECT department, PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY salary) as p25, PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) as p50, PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY salary) as p75 FROM data GROUP BY department"
                    )
                else:
                    return Mock(content="SELECT * FROM data LIMIT 100")

            mock_llm.invoke.side_effect = mock_sql_response
            mock_openai.return_value = mock_llm

            with patch("services.langchain_service.duckdb_service") as mock_duckdb:
                # Mock DuckDB responses with realistic execution times
                def mock_query_execution(project_id, sql_query):
                    # Simulate different execution times based on query complexity
                    if "GROUP BY" in sql_query.upper():
                        time.sleep(0.5)  # Aggregation queries are slower
                        return ([{"department": "Engineering", "avg_salary": 75000}], 0.5, 1)
                    elif "PERCENTILE" in sql_query.upper():
                        time.sleep(1.0)  # Statistical queries are slowest
                        return (
                            [
                                {
                                    "department": "Engineering",
                                    "p25": 65000,
                                    "p50": 75000,
                                    "p75": 85000,
                                }
                            ],
                            1.0,
                            1,
                        )
                    elif "WHERE" in sql_query.upper():
                        time.sleep(0.2)  # Filtered queries are moderate
                        return ([{"id": 1, "name": "John", "salary": 75000}], 0.2, 1)
                    else:
                        time.sleep(0.1)  # Simple queries are fast
                        return ([{"id": 1, "name": "John"}], 0.1, 1)

                mock_duckdb.execute_query.side_effect = mock_query_execution
                mock_duckdb.validate_sql_query.return_value = (True, "")

                # Test each query type
                for query_name, query_text in test_queries:
                    metrics = self.measure_operation(
                        f"LangChain Query: {query_name}",
                        self.langchain_service.process_query,
                        query_text,
                        str(test_project.id),
                        str(test_user.id),
                    )

                    query_performance_results.append(
                        {
                            "query_name": query_name,
                            "query_text": query_text,
                            "execution_time": metrics.execution_time,
                            "success": metrics.success,
                            "memory_usage": metrics.memory_usage_mb,
                        }
                    )

        # Clean up
        self.project_service.delete_project(test_project.id)
        self.user_service.delete_user(test_user.id)

        return query_performance_results

    def test_concurrent_query_processing(self, concurrent_queries: int = 10):
        """Test concurrent query processing performance"""
        test_user, test_project = self.create_test_project_with_data()

        import concurrent.futures
        import threading

        def process_single_query(query_id: int):
            """Process a single query in a thread"""
            with (
                patch("services.langchain_service.ChatOpenAI") as mock_openai,
                patch("services.langchain_service.duckdb_service") as mock_duckdb,
            ):

                mock_llm = Mock()
                mock_llm.invoke.return_value = Mock(
                    content=f"SELECT * FROM data WHERE id = {query_id}"
                )
                mock_openai.return_value = mock_llm

                mock_duckdb.execute_query.return_value = (
                    [{"id": query_id, "name": f"User {query_id}"}],
                    0.1,
                    1,
                )
                mock_duckdb.validate_sql_query.return_value = (True, "")

                start_time = time.time()
                try:
                    result = self.langchain_service.process_query(
                        f"Show me user with id {query_id}", str(test_project.id), str(test_user.id)
                    )
                    success = True
                except Exception as e:
                    success = False
                    result = str(e)

                end_time = time.time()

                return {
                    "query_id": query_id,
                    "execution_time": end_time - start_time,
                    "success": success,
                    "thread_id": threading.current_thread().ident,
                }

        # Execute concurrent queries
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_queries) as executor:
            futures = [executor.submit(process_single_query, i) for i in range(concurrent_queries)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        end_time = time.time()
        total_time = end_time - start_time

        # Clean up
        self.project_service.delete_project(test_project.id)
        self.user_service.delete_user(test_user.id)

        # Analyze concurrent performance
        successful_queries = [r for r in results if r["success"]]
        avg_query_time = (
            sum(r["execution_time"] for r in successful_queries) / len(successful_queries)
            if successful_queries
            else 0
        )

        concurrent_performance = {
            "total_queries": concurrent_queries,
            "successful_queries": len(successful_queries),
            "failed_queries": concurrent_queries - len(successful_queries),
            "total_execution_time": total_time,
            "average_query_time": avg_query_time,
            "queries_per_second": concurrent_queries / total_time,
            "concurrent_efficiency": (
                (concurrent_queries / total_time) / (1 / avg_query_time)
                if avg_query_time > 0
                else 0
            ),
        }

        return concurrent_performance, results

    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        print("\n" + "=" * 80)
        print("QUERY PERFORMANCE ANALYSIS REPORT")
        print("=" * 80)

        if not self.metrics:
            print("No performance metrics collected.")
            return

        # Overall statistics
        successful_operations = [m for m in self.metrics if m.success]
        failed_operations = [m for m in self.metrics if not m.success]

        print(f"\nOperation Summary:")
        print(f"  Total Operations: {len(self.metrics)}")
        print(f"  Successful: {len(successful_operations)}")
        print(f"  Failed: {len(failed_operations)}")
        print(f"  Success Rate: {len(successful_operations) / len(self.metrics) * 100:.1f}%")

        if successful_operations:
            execution_times = [m.execution_time for m in successful_operations]
            memory_usage = [
                m.memory_usage_mb for m in successful_operations if m.memory_usage_mb > 0
            ]

            print(f"\nPerformance Metrics:")
            print(f"  Average Execution Time: {sum(execution_times) / len(execution_times):.3f}s")
            print(f"  Fastest Operation: {min(execution_times):.3f}s")
            print(f"  Slowest Operation: {max(execution_times):.3f}s")

            if memory_usage:
                print(f"  Average Memory Usage: {sum(memory_usage) / len(memory_usage):.2f}MB")
                print(f"  Max Memory Usage: {max(memory_usage):.2f}MB")

        # Detailed operation breakdown
        print(f"\nDetailed Operation Performance:")
        print("-" * 80)
        print(f"{'Operation':<40} {'Time (s)':<10} {'Memory (MB)':<12} {'Status':<10}")
        print("-" * 80)

        for metric in self.metrics:
            status = "SUCCESS" if metric.success else "FAILED"
            memory_str = f"{metric.memory_usage_mb:.2f}" if metric.memory_usage_mb > 0 else "N/A"
            print(
                f"{metric.operation:<40} {metric.execution_time:<10.3f} {memory_str:<12} {status:<10}"
            )

        if failed_operations:
            print(f"\nError Details:")
            for metric in failed_operations:
                print(f"  {metric.operation}: {metric.error_message}")

        print("\n" + "=" * 80)


def run_query_performance_tests():
    """Run comprehensive query performance tests"""
    tester = QueryPerformanceTester()

    print("Starting Query Performance Testing Suite")
    print("=" * 80)

    # Test 1: Individual query processing performance
    print("\n1. Testing Individual Query Processing Performance...")
    query_results = tester.test_langchain_query_processing_performance()

    print("\nQuery Performance Results:")
    print("-" * 60)
    for result in query_results:
        status = "✓" if result["success"] else "✗"
        print(
            f"{status} {result['query_name']:<30} {result['execution_time']:.3f}s {result['memory_usage']:>8.2f}MB"
        )

    # Test 2: Concurrent query processing
    print("\n2. Testing Concurrent Query Processing...")
    concurrent_perf, concurrent_results = tester.test_concurrent_query_processing(
        concurrent_queries=5
    )

    print(f"\nConcurrent Performance Results:")
    print(f"  Total Queries: {concurrent_perf['total_queries']}")
    print(f"  Successful: {concurrent_perf['successful_queries']}")
    print(f"  Average Query Time: {concurrent_perf['average_query_time']:.3f}s")
    print(f"  Queries per Second: {concurrent_perf['queries_per_second']:.2f}")
    print(f"  Concurrent Efficiency: {concurrent_perf['concurrent_efficiency']:.2f}")

    # Generate comprehensive report
    tester.generate_performance_report()

    return tester


if __name__ == "__main__":
    # Run query performance tests
    run_query_performance_tests()
