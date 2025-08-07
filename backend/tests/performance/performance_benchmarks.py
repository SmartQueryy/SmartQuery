"""
Performance Benchmarks and Optimization - Task B27

Establishes performance benchmarks for SmartQuery API and provides
optimization recommendations based on measured performance.
"""

import json
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests


@dataclass
class PerformanceBenchmark:
    """Performance benchmark definition"""

    endpoint: str
    operation: str
    target_response_time: float  # seconds
    max_acceptable_time: float  # seconds
    target_throughput: float  # requests per second
    max_error_rate: float  # percentage
    memory_limit_mb: float  # megabytes


@dataclass
class BenchmarkResult:
    """Result of benchmark testing"""

    benchmark: PerformanceBenchmark
    actual_response_time: float
    actual_throughput: float
    actual_error_rate: float
    actual_memory_usage: float
    passes_benchmark: bool
    optimization_priority: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"


class PerformanceBenchmarkSuite:
    """Performance benchmarking and optimization analysis"""

    def __init__(self):
        self.benchmarks = self._define_performance_benchmarks()
        self.results: List[BenchmarkResult] = []

    def _define_performance_benchmarks(self) -> List[PerformanceBenchmark]:
        """Define performance benchmarks for all API endpoints"""
        return [
            # System Health Endpoints
            PerformanceBenchmark(
                endpoint="/",
                operation="Root endpoint",
                target_response_time=0.050,  # 50ms
                max_acceptable_time=0.200,  # 200ms
                target_throughput=100.0,  # 100 RPS
                max_error_rate=0.1,  # 0.1%
                memory_limit_mb=10.0,  # 10MB
            ),
            PerformanceBenchmark(
                endpoint="/health",
                operation="Health check",
                target_response_time=0.100,  # 100ms
                max_acceptable_time=0.500,  # 500ms
                target_throughput=50.0,  # 50 RPS
                max_error_rate=1.0,  # 1%
                memory_limit_mb=20.0,  # 20MB
            ),
            # Authentication Endpoints
            PerformanceBenchmark(
                endpoint="/auth/me",
                operation="Get user profile",
                target_response_time=0.200,  # 200ms
                max_acceptable_time=1.000,  # 1s
                target_throughput=30.0,  # 30 RPS
                max_error_rate=2.0,  # 2%
                memory_limit_mb=15.0,  # 15MB
            ),
            # Project Management Endpoints
            PerformanceBenchmark(
                endpoint="/projects",
                operation="List projects",
                target_response_time=0.300,  # 300ms
                max_acceptable_time=1.500,  # 1.5s
                target_throughput=20.0,  # 20 RPS
                max_error_rate=2.0,  # 2%
                memory_limit_mb=30.0,  # 30MB
            ),
            PerformanceBenchmark(
                endpoint="/projects",
                operation="Create project",
                target_response_time=0.500,  # 500ms
                max_acceptable_time=2.000,  # 2s
                target_throughput=10.0,  # 10 RPS
                max_error_rate=3.0,  # 3%
                memory_limit_mb=50.0,  # 50MB
            ),
            # Chat/Query Processing Endpoints (Most Critical)
            PerformanceBenchmark(
                endpoint="/chat/{project_id}/preview",
                operation="CSV preview",
                target_response_time=1.000,  # 1s
                max_acceptable_time=3.000,  # 3s
                target_throughput=5.0,  # 5 RPS
                max_error_rate=5.0,  # 5%
                memory_limit_mb=100.0,  # 100MB
            ),
            PerformanceBenchmark(
                endpoint="/chat/{project_id}/message",
                operation="Process query (Simple)",
                target_response_time=2.000,  # 2s
                max_acceptable_time=8.000,  # 8s
                target_throughput=2.0,  # 2 RPS
                max_error_rate=10.0,  # 10%
                memory_limit_mb=200.0,  # 200MB
            ),
            PerformanceBenchmark(
                endpoint="/chat/{project_id}/message",
                operation="Process query (Complex)",
                target_response_time=5.000,  # 5s
                max_acceptable_time=15.000,  # 15s
                target_throughput=1.0,  # 1 RPS
                max_error_rate=15.0,  # 15%
                memory_limit_mb=300.0,  # 300MB
            ),
            PerformanceBenchmark(
                endpoint="/chat/{project_id}/suggestions",
                operation="Generate suggestions",
                target_response_time=1.500,  # 1.5s
                max_acceptable_time=5.000,  # 5s
                target_throughput=3.0,  # 3 RPS
                max_error_rate=8.0,  # 8%
                memory_limit_mb=150.0,  # 150MB
            ),
        ]

    def evaluate_benchmark(
        self,
        benchmark: PerformanceBenchmark,
        actual_response_time: float,
        actual_throughput: float,
        actual_error_rate: float,
        actual_memory_usage: float = 0.0,
    ) -> BenchmarkResult:
        """Evaluate actual performance against benchmark"""

        # Determine if benchmark passes
        passes_response_time = actual_response_time <= benchmark.max_acceptable_time
        passes_error_rate = actual_error_rate <= benchmark.max_error_rate
        passes_memory = (
            actual_memory_usage <= benchmark.memory_limit_mb or actual_memory_usage == 0.0
        )

        passes_benchmark = passes_response_time and passes_error_rate and passes_memory

        # Determine optimization priority
        if not passes_benchmark:
            if actual_response_time > benchmark.max_acceptable_time * 2:
                priority = "CRITICAL"
            elif actual_response_time > benchmark.max_acceptable_time * 1.5:
                priority = "HIGH"
            elif actual_response_time > benchmark.target_response_time * 2:
                priority = "MEDIUM"
            else:
                priority = "LOW"
        elif actual_response_time > benchmark.target_response_time:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        return BenchmarkResult(
            benchmark=benchmark,
            actual_response_time=actual_response_time,
            actual_throughput=actual_throughput,
            actual_error_rate=actual_error_rate,
            actual_memory_usage=actual_memory_usage,
            passes_benchmark=passes_benchmark,
            optimization_priority=priority,
        )

    def generate_optimization_recommendations(self) -> Dict[str, List[str]]:
        """Generate optimization recommendations based on benchmark results"""
        recommendations = {"CRITICAL": [], "HIGH": [], "MEDIUM": [], "LOW": []}

        critical_endpoints = [r for r in self.results if r.optimization_priority == "CRITICAL"]
        high_priority_endpoints = [r for r in self.results if r.optimization_priority == "HIGH"]
        medium_priority_endpoints = [r for r in self.results if r.optimization_priority == "MEDIUM"]

        # Critical optimizations
        for result in critical_endpoints:
            if "query" in result.benchmark.operation.lower():
                recommendations["CRITICAL"].extend(
                    [
                        f"URGENT: Optimize {result.benchmark.endpoint} - Response time {result.actual_response_time:.2f}s exceeds limit",
                        "Consider implementing query result caching",
                        "Optimize OpenAI API calls with response caching",
                        "Implement async processing for complex queries",
                        "Add query timeout and circuit breakers",
                    ]
                )
            elif "preview" in result.benchmark.operation.lower():
                recommendations["CRITICAL"].extend(
                    [
                        f"URGENT: Optimize CSV preview loading for {result.benchmark.endpoint}",
                        "Implement CSV preview caching",
                        "Use streaming for large file previews",
                        "Add pagination to preview data",
                    ]
                )

        # High priority optimizations
        for result in high_priority_endpoints:
            if result.actual_response_time > result.benchmark.target_response_time * 3:
                recommendations["HIGH"].append(
                    f"Optimize {result.benchmark.endpoint}: {result.actual_response_time:.2f}s response time"
                )

        # Medium priority optimizations
        if (
            len(
                [
                    r
                    for r in self.results
                    if r.actual_response_time > r.benchmark.target_response_time
                ]
            )
            > 0
        ):
            recommendations["MEDIUM"].extend(
                [
                    "Implement Redis caching for frequent queries",
                    "Add database connection pooling",
                    "Optimize database queries with proper indexing",
                    "Implement request/response compression",
                    "Add CDN for static content delivery",
                ]
            )

        # General optimizations
        recommendations["LOW"].extend(
            [
                "Implement API response pagination",
                "Add request rate limiting",
                "Optimize JSON serialization/deserialization",
                "Monitor and optimize memory usage",
                "Implement graceful degradation for external service failures",
            ]
        )

        return recommendations

    def generate_benchmark_report(self) -> str:
        """Generate comprehensive benchmark report"""
        if not self.results:
            return "No benchmark results available"

        report = []
        report.append("=" * 100)
        report.append("SMARTQUERY API PERFORMANCE BENCHMARK REPORT")
        report.append("=" * 100)

        # Summary statistics
        total_benchmarks = len(self.results)
        passing_benchmarks = len([r for r in self.results if r.passes_benchmark])
        critical_issues = len([r for r in self.results if r.optimization_priority == "CRITICAL"])
        high_priority_issues = len([r for r in self.results if r.optimization_priority == "HIGH"])

        report.append(f"\nBENCHMARK SUMMARY:")
        report.append(f"  Total Benchmarks: {total_benchmarks}")
        report.append(
            f"  Passing: {passing_benchmarks} ({passing_benchmarks/total_benchmarks*100:.1f}%)"
        )
        report.append(f"  Failing: {total_benchmarks - passing_benchmarks}")
        report.append(f"  Critical Issues: {critical_issues}")
        report.append(f"  High Priority Issues: {high_priority_issues}")

        # Detailed results
        report.append(f"\nDETAILED BENCHMARK RESULTS:")
        report.append("-" * 100)
        report.append(
            f"{'Endpoint':<35} {'Operation':<20} {'Target':<8} {'Actual':<8} {'Status':<8} {'Priority':<8}"
        )
        report.append("-" * 100)

        for result in sorted(self.results, key=lambda x: x.actual_response_time, reverse=True):
            status = "PASS" if result.passes_benchmark else "FAIL"
            target_time = f"{result.benchmark.target_response_time:.2f}s"
            actual_time = f"{result.actual_response_time:.2f}s"
            endpoint = result.benchmark.endpoint[:34]
            operation = result.benchmark.operation[:19]

            report.append(
                f"{endpoint:<35} {operation:<20} {target_time:<8} {actual_time:<8} {status:<8} {result.optimization_priority:<8}"
            )

        # Performance categories analysis
        report.append(f"\nPERFORMANCE ANALYSIS BY CATEGORY:")
        report.append("-" * 50)

        categories = {
            "System Health": ["/", "/health"],
            "Authentication": ["/auth/me"],
            "Project Management": ["/projects"],
            "Query Processing": ["/chat"],
        }

        for category, endpoints in categories.items():
            category_results = [
                r for r in self.results if any(ep in r.benchmark.endpoint for ep in endpoints)
            ]
            if category_results:
                avg_response_time = sum(r.actual_response_time for r in category_results) / len(
                    category_results
                )
                passing_rate = (
                    len([r for r in category_results if r.passes_benchmark])
                    / len(category_results)
                    * 100
                )

                report.append(
                    f"{category:<20}: Avg {avg_response_time:.3f}s, {passing_rate:.0f}% passing"
                )

        # Optimization recommendations
        recommendations = self.generate_optimization_recommendations()

        report.append(f"\nOPTIMIZATION RECOMMENDATIONS:")
        report.append("-" * 50)

        for priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            if recommendations[priority]:
                report.append(f"\n{priority} Priority:")
                for recommendation in recommendations[priority]:
                    report.append(f"  • {recommendation}")

        # Performance targets vs actual
        report.append(f"\nPERFORMANCE TARGETS VS ACTUAL:")
        report.append("-" * 50)

        query_processing_results = [
            r for r in self.results if "query" in r.benchmark.operation.lower()
        ]
        if query_processing_results:
            avg_query_time = sum(r.actual_response_time for r in query_processing_results) / len(
                query_processing_results
            )
            target_query_time = sum(
                r.benchmark.target_response_time for r in query_processing_results
            ) / len(query_processing_results)

            report.append(f"Query Processing:")
            report.append(f"  Target Avg: {target_query_time:.2f}s")
            report.append(f"  Actual Avg: {avg_query_time:.2f}s")
            report.append(
                f"  Performance Gap: {((avg_query_time - target_query_time) / target_query_time * 100):+.1f}%"
            )

        report.append("\n" + "=" * 100)

        return "\n".join(report)

    def save_benchmark_results(self, filename: str):
        """Save benchmark results to JSON file"""
        results_data = []

        for result in self.results:
            results_data.append(
                {
                    "endpoint": result.benchmark.endpoint,
                    "operation": result.benchmark.operation,
                    "target_response_time": result.benchmark.target_response_time,
                    "max_acceptable_time": result.benchmark.max_acceptable_time,
                    "actual_response_time": result.actual_response_time,
                    "actual_throughput": result.actual_throughput,
                    "actual_error_rate": result.actual_error_rate,
                    "passes_benchmark": result.passes_benchmark,
                    "optimization_priority": result.optimization_priority,
                    "timestamp": time.time(),
                }
            )

        with open(filename, "w") as f:
            json.dump(
                {
                    "benchmark_run_timestamp": time.time(),
                    "total_benchmarks": len(self.results),
                    "passing_benchmarks": len([r for r in self.results if r.passes_benchmark]),
                    "results": results_data,
                },
                f,
                indent=2,
            )


def create_performance_optimization_plan() -> str:
    """Create comprehensive performance optimization plan"""

    optimization_plan = """
SMARTQUERY PERFORMANCE OPTIMIZATION PLAN
========================================

PHASE 1: CRITICAL PERFORMANCE ISSUES (Week 1)
---------------------------------------------
1. Query Processing Pipeline Optimization
   - Implement query result caching with Redis
   - Add OpenAI response caching for similar queries  
   - Implement query timeout mechanisms (15s max)
   - Add circuit breakers for external API failures

2. Database Query Optimization
   - Add proper database indexing for user_id, project_id lookups
   - Implement connection pooling for PostgreSQL
   - Optimize DuckDB query execution with prepared statements
   - Add query performance monitoring and slow query logging

3. Memory Usage Optimization
   - Implement CSV streaming for large file processing
   - Add memory limits and garbage collection for query processing
   - Optimize LangChain memory usage during query processing
   - Implement request-scoped memory monitoring

PHASE 2: HIGH PRIORITY OPTIMIZATIONS (Week 2-3)
----------------------------------------------
1. API Response Optimization
   - Implement response compression (gzip)
   - Add pagination for list endpoints
   - Optimize JSON serialization with orjson
   - Implement partial response patterns for large data sets

2. Caching Strategy Implementation
   - Redis caching for user authentication data
   - Project metadata caching with TTL
   - CSV preview data caching
   - Query suggestion caching per project

3. Async Processing Implementation
   - Background processing for complex queries using Celery
   - Async file upload processing
   - Non-blocking CSV schema analysis
   - WebSocket support for real-time query progress

PHASE 3: MEDIUM PRIORITY IMPROVEMENTS (Week 4)
---------------------------------------------
1. Infrastructure Optimization
   - CDN implementation for static assets
   - Load balancing for multiple API instances
   - Database read replicas for query-heavy operations
   - Implement health checks with dependency monitoring

2. Monitoring and Observability
   - Comprehensive performance metrics collection
   - APM (Application Performance Monitoring) integration
   - Real-time performance alerting
   - Performance regression testing in CI/CD

PERFORMANCE TARGETS AFTER OPTIMIZATION:
--------------------------------------
- System Health Endpoints: < 50ms response time
- Authentication: < 200ms response time  
- Project Management: < 300ms response time
- Simple Queries: < 2s response time
- Complex Queries: < 5s response time
- API Error Rate: < 2% overall
- Concurrent Users: Support 50+ simultaneous users
- Memory Usage: < 500MB per worker process

MONITORING AND VALIDATION:
-------------------------
- Daily performance regression tests
- Weekly performance benchmark reports  
- Monthly performance review and optimization
- Continuous monitoring of P95 response times
- Alert on performance degradation > 20%

EXPECTED OUTCOMES:
-----------------
- 70% reduction in average query processing time
- 90% reduction in memory usage for CSV processing
- 95% reduction in API timeout errors
- Support for 10x current concurrent user load
- Improved user satisfaction with faster responses
"""

    return optimization_plan


if __name__ == "__main__":
    # Initialize benchmark suite
    benchmark_suite = PerformanceBenchmarkSuite()

    # Print benchmark definitions
    print("SmartQuery Performance Benchmarks:")
    print("=" * 60)

    for benchmark in benchmark_suite.benchmarks:
        print(
            f"{benchmark.endpoint:<30} | Target: {benchmark.target_response_time}s | Max: {benchmark.max_acceptable_time}s"
        )

    print("\nPerformance Optimization Plan:")
    print(create_performance_optimization_plan())
