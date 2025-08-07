"""
Performance Load Testing Suite - Task B27

Comprehensive load testing for SmartQuery API endpoints to identify bottlenecks
and ensure the system meets performance requirements under load.
"""

import asyncio
import json
import os
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests


@dataclass
class LoadTestResult:
    """Results from a load test run"""

    endpoint: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    min_response_time: float
    max_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    requests_per_second: float
    error_rate: float
    errors: List[str]


class LoadTester:
    """Load testing utility for SmartQuery API"""

    def __init__(self, base_url: str = "http://localhost:8000", auth_token: str = None):
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self.session = requests.Session()

        if auth_token:
            self.session.headers.update({"Authorization": f"Bearer {auth_token}"})

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make a single HTTP request and measure response time"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()

        try:
            response = self.session.request(method, url, **kwargs)
            end_time = time.time()

            return {
                "success": True,
                "response_time": end_time - start_time,
                "status_code": response.status_code,
                "response_size": len(response.content),
                "error": None,
            }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "response_time": end_time - start_time,
                "status_code": 0,
                "response_size": 0,
                "error": str(e),
            }

    def run_load_test(
        self,
        endpoint: str,
        method: str = "GET",
        num_requests: int = 100,
        concurrent_users: int = 10,
        **request_kwargs,
    ) -> LoadTestResult:
        """Run load test on a specific endpoint"""
        print(f"Starting load test: {method} {endpoint}")
        print(f"Requests: {num_requests}, Concurrent users: {concurrent_users}")

        start_time = time.time()
        results = []
        errors = []

        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            # Submit all requests
            futures = [
                executor.submit(self._make_request, method, endpoint, **request_kwargs)
                for _ in range(num_requests)
            ]

            # Collect results
            for future in as_completed(futures):
                result = future.result()
                results.append(result)

                if not result["success"]:
                    errors.append(result["error"])

        end_time = time.time()
        total_duration = end_time - start_time

        # Calculate statistics
        successful_results = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in successful_results]

        if response_times:
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            median_time = statistics.median(response_times)
            p95_time = self._percentile(response_times, 0.95)
            p99_time = self._percentile(response_times, 0.99)
        else:
            avg_time = min_time = max_time = median_time = p95_time = p99_time = 0

        return LoadTestResult(
            endpoint=f"{method} {endpoint}",
            total_requests=num_requests,
            successful_requests=len(successful_results),
            failed_requests=len(results) - len(successful_results),
            average_response_time=avg_time,
            min_response_time=min_time,
            max_response_time=max_time,
            median_response_time=median_time,
            p95_response_time=p95_time,
            p99_response_time=p99_time,
            requests_per_second=num_requests / total_duration,
            error_rate=(len(results) - len(successful_results)) / len(results) * 100,
            errors=errors[:10],  # Keep only first 10 errors
        )

    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile value"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile)
        if index >= len(sorted_data):
            index = len(sorted_data) - 1
        return sorted_data[index]

    def print_results(self, result: LoadTestResult):
        """Pretty print load test results"""
        print(f"\n{'=' * 60}")
        print(f"LOAD TEST RESULTS: {result.endpoint}")
        print(f"{'=' * 60}")
        print(f"Total Requests:      {result.total_requests}")
        print(f"Successful:          {result.successful_requests}")
        print(f"Failed:              {result.failed_requests}")
        print(f"Error Rate:          {result.error_rate:.2f}%")
        print(f"Requests/Second:     {result.requests_per_second:.2f}")
        print(f"\nResponse Times (seconds):")
        print(f"  Average:           {result.average_response_time:.3f}")
        print(f"  Median:            {result.median_response_time:.3f}")
        print(f"  Min:               {result.min_response_time:.3f}")
        print(f"  Max:               {result.max_response_time:.3f}")
        print(f"  95th percentile:   {result.p95_response_time:.3f}")
        print(f"  99th percentile:   {result.p99_response_time:.3f}")

        if result.errors:
            print(f"\nFirst {len(result.errors)} errors:")
            for error in result.errors:
                print(f"  - {error}")
        print()


def run_comprehensive_load_tests():
    """Run comprehensive load tests on all major endpoints"""
    load_tester = LoadTester()

    # Test configurations for different scenarios
    test_configs = [
        # Light load tests
        {"name": "Light Load", "requests": 50, "concurrent": 5},
        # Moderate load tests
        {"name": "Moderate Load", "requests": 200, "concurrent": 20},
        # Heavy load tests
        {"name": "Heavy Load", "requests": 500, "concurrent": 50},
    ]

    # Endpoints to test
    endpoints_to_test = [
        {"method": "GET", "endpoint": "/", "name": "Root"},
        {"method": "GET", "endpoint": "/health", "name": "Health Check"},
        {"method": "GET", "endpoint": "/auth/me", "name": "Auth Me (requires auth)"},
        {"method": "GET", "endpoint": "/projects", "name": "List Projects (requires auth)"},
        # Add more endpoints as needed
    ]

    all_results = []

    print("Starting Comprehensive Load Testing Suite")
    print("=" * 80)

    for config in test_configs:
        print(f"\n{config['name']} Testing Phase")
        print("-" * 40)

        for endpoint_config in endpoints_to_test:
            # Skip auth endpoints for now in comprehensive test
            if "requires auth" in endpoint_config["name"]:
                print(f"Skipping {endpoint_config['name']} (requires authentication)")
                continue

            result = load_tester.run_load_test(
                endpoint=endpoint_config["endpoint"],
                method=endpoint_config["method"],
                num_requests=config["requests"],
                concurrent_users=config["concurrent"],
            )

            load_tester.print_results(result)
            all_results.append(result)

    # Generate summary report
    generate_performance_report(all_results)


def generate_performance_report(results: List[LoadTestResult]):
    """Generate comprehensive performance report"""
    print("\n" + "=" * 80)
    print("COMPREHENSIVE PERFORMANCE REPORT")
    print("=" * 80)

    # Performance benchmarks (in seconds)
    performance_benchmarks = {
        "excellent": 0.1,  # < 100ms
        "good": 0.5,  # < 500ms
        "acceptable": 2.0,  # < 2s
        "poor": 5.0,  # < 5s
    }

    print("\nPerformance Benchmarks:")
    print(f"  Excellent:  < {performance_benchmarks['excellent']}s")
    print(f"  Good:       < {performance_benchmarks['good']}s")
    print(f"  Acceptable: < {performance_benchmarks['acceptable']}s")
    print(f"  Poor:       < {performance_benchmarks['poor']}s")
    print(f"  Critical:   >= {performance_benchmarks['poor']}s")

    print("\nEndpoint Performance Summary:")
    print("-" * 80)

    for result in results:
        # Determine performance rating
        avg_time = result.average_response_time
        if avg_time < performance_benchmarks["excellent"]:
            rating = "EXCELLENT"
        elif avg_time < performance_benchmarks["good"]:
            rating = "GOOD"
        elif avg_time < performance_benchmarks["acceptable"]:
            rating = "ACCEPTABLE"
        elif avg_time < performance_benchmarks["poor"]:
            rating = "POOR"
        else:
            rating = "CRITICAL"

        print(
            f"{result.endpoint:35} | {rating:10} | "
            f"Avg: {avg_time:6.3f}s | P95: {result.p95_response_time:6.3f}s | "
            f"RPS: {result.requests_per_second:6.1f} | "
            f"Error Rate: {result.error_rate:5.1f}%"
        )

    # Identify bottlenecks
    print("\nBottleneck Analysis:")
    print("-" * 40)

    slow_endpoints = [
        r for r in results if r.average_response_time > performance_benchmarks["good"]
    ]
    if slow_endpoints:
        print("Endpoints requiring optimization:")
        for result in sorted(slow_endpoints, key=lambda x: x.average_response_time, reverse=True):
            print(f"  - {result.endpoint}: {result.average_response_time:.3f}s avg")
    else:
        print("All endpoints meet performance benchmarks!")

    # High error rate analysis
    high_error_endpoints = [r for r in results if r.error_rate > 5.0]
    if high_error_endpoints:
        print("\nEndpoints with high error rates (>5%):")
        for result in high_error_endpoints:
            print(f"  - {result.endpoint}: {result.error_rate:.1f}% error rate")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    # Run comprehensive load tests
    run_comprehensive_load_tests()
