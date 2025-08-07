"""
Performance Testing Suite for SmartQuery API - Task B27

This package contains comprehensive performance testing tools including:
- Load testing for API endpoints
- Query processing performance analysis
- Memory profiling and optimization
- Performance benchmarking and reporting
- Optimization recommendations
"""

from .load_testing import LoadTester, run_comprehensive_load_tests
from .performance_benchmarks import PerformanceBenchmarkSuite, create_performance_optimization_plan
from .query_performance_test import QueryPerformanceTester, run_query_performance_tests
from .run_performance_tests import main as run_all_performance_tests

__all__ = [
    "LoadTester",
    "run_comprehensive_load_tests",
    "PerformanceBenchmarkSuite",
    "create_performance_optimization_plan",
    "QueryPerformanceTester",
    "run_query_performance_tests",
    "run_all_performance_tests",
]
