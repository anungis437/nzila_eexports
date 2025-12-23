"""
Performance tests for financial API endpoints.

Tests response times, database query counts, and load handling
to ensure the API meets performance requirements.

Target Metrics:
- Response time: < 200ms for GET requests
- Response time: < 500ms for POST requests  
- Query count: < 10 queries per request (avoid N+1)
- Concurrent requests: 10+ requests/second throughput
"""

import time
from decimal import Decimal
from django.test import TestCase, TransactionTestCase
from django.test.utils import override_settings
from django.urls import reverse
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework import status
from rest_framework.test import APIClient
from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import mean, median, stdev

from tests.factories import (
    UserFactory,
    DealFactory,
    CurrencyFactory,
    DealFinancialTermsFactory,
    FinancingOptionFactory,
    PaymentMilestoneFactory,
)
from deals.models import DealFinancialTerms, FinancingOption, PaymentMilestone


class FinancialAPIResponseTimeTest(TestCase):
    """Test response times for financial API endpoints."""
    
    # Target response times (in seconds)
    GET_TARGET = 0.200  # 200ms for GET requests
    POST_TARGET = 0.500  # 500ms for POST requests
    
    def setUp(self):
        self.client = APIClient()
        self.buyer = UserFactory(role='buyer')
        self.dealer = UserFactory(role='dealer')
        self.currency = CurrencyFactory(code='USD')
        
        # Create test deal with financial data
        self.deal = DealFactory(buyer=self.buyer, dealer=self.dealer)
        self.terms = DealFinancialTermsFactory(
            deal=self.deal,
            currency=self.currency,
            total_price=Decimal('50000')
        )
        
        # Create payment milestones
        for i in range(5):
            PaymentMilestoneFactory(
                deal_financial_terms=self.terms,
                amount_due=Decimal('10000')
            )
        
        # Create financing
        self.financing = FinancingOptionFactory(deal=self.deal)
        
        self.client.force_authenticate(user=self.buyer)
    
    def _benchmark_request(self, method, url, data=None, iterations=10):
        """
        Benchmark an API request over multiple iterations.
        
        Returns:
            dict: Statistics including min, max, mean, median, stdev
        """
        times = []
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            
            if method == 'GET':
                response = self.client.get(url)
            elif method == 'POST':
                response = self.client.post(url, data, format='json')
            
            end_time = time.perf_counter()
            elapsed = end_time - start_time
            times.append(elapsed)
            
            # Verify request succeeded
            self.assertIn(response.status_code, [
                status.HTTP_200_OK,
                status.HTTP_201_CREATED
            ])
        
        return {
            'min': min(times),
            'max': max(times),
            'mean': mean(times),
            'median': median(times),
            'stdev': stdev(times) if len(times) > 1 else 0,
            'samples': len(times)
        }
    
    def test_financial_terms_response_time(self):
        """Test GET /api/deals/{id}/financial-terms/ response time."""
        url = reverse('deal-financial-terms', kwargs={'pk': self.deal.id})
        stats = self._benchmark_request('GET', url, iterations=20)
        
        print(f"\n[Financial Terms Endpoint]")
        print(f"  Mean: {stats['mean']*1000:.2f}ms")
        print(f"  Median: {stats['median']*1000:.2f}ms")
        print(f"  Min: {stats['min']*1000:.2f}ms")
        print(f"  Max: {stats['max']*1000:.2f}ms")
        print(f"  StdDev: {stats['stdev']*1000:.2f}ms")
        
        # Verify meets performance target
        self.assertLess(
            stats['mean'],
            self.GET_TARGET,
            f"Mean response time {stats['mean']*1000:.2f}ms exceeds {self.GET_TARGET*1000}ms target"
        )
    
    def test_payment_schedule_response_time(self):
        """Test GET /api/deals/{id}/payment-schedule/ response time."""
        url = reverse('deal-payment-schedule', kwargs={'pk': self.deal.id})
        stats = self._benchmark_request('GET', url, iterations=20)
        
        print(f"\n[Payment Schedule Endpoint]")
        print(f"  Mean: {stats['mean']*1000:.2f}ms")
        print(f"  Median: {stats['median']*1000:.2f}ms")
        print(f"  Min: {stats['min']*1000:.2f}ms")
        print(f"  Max: {stats['max']*1000:.2f}ms")
        print(f"  StdDev: {stats['stdev']*1000:.2f}ms")
        
        self.assertLess(
            stats['mean'],
            self.GET_TARGET,
            f"Mean response time {stats['mean']*1000:.2f}ms exceeds {self.GET_TARGET*1000}ms target"
        )
    
    def test_financing_response_time(self):
        """Test GET /api/deals/{id}/financing/ response time."""
        url = reverse('deal-financing', kwargs={'pk': self.deal.id})
        stats = self._benchmark_request('GET', url, iterations=20)
        
        print(f"\n[Financing Endpoint]")
        print(f"  Mean: {stats['mean']*1000:.2f}ms")
        print(f"  Median: {stats['median']*1000:.2f}ms")
        print(f"  Min: {stats['min']*1000:.2f}ms")
        print(f"  Max: {stats['max']*1000:.2f}ms")
        print(f"  StdDev: {stats['stdev']*1000:.2f}ms")
        
        self.assertLess(
            stats['mean'],
            self.GET_TARGET,
            f"Mean response time {stats['mean']*1000:.2f}ms exceeds {self.GET_TARGET*1000}ms target"
        )
    
    def test_process_payment_response_time(self):
        """Test POST /api/deals/{id}/process-payment/ response time."""
        url = reverse('deal-process-payment', kwargs={'pk': self.deal.id})
        payment_data = {'amount': '5000.00'}
        
        stats = self._benchmark_request('POST', url, payment_data, iterations=10)
        
        print(f"\n[Process Payment Endpoint]")
        print(f"  Mean: {stats['mean']*1000:.2f}ms")
        print(f"  Median: {stats['median']*1000:.2f}ms")
        print(f"  Min: {stats['min']*1000:.2f}ms")
        print(f"  Max: {stats['max']*1000:.2f}ms")
        print(f"  StdDev: {stats['stdev']*1000:.2f}ms")
        
        self.assertLess(
            stats['mean'],
            self.POST_TARGET,
            f"Mean response time {stats['mean']*1000:.2f}ms exceeds {self.POST_TARGET*1000}ms target"
        )


class DatabaseQueryEfficiencyTest(TestCase):
    """Test database query counts and efficiency."""
    
    # Target query counts
    MAX_QUERIES_GET = 10  # Maximum queries for GET requests
    MAX_QUERIES_POST = 25  # Maximum queries for POST requests (includes notifications, updates)
    
    def setUp(self):
        self.client = APIClient()
        self.buyer = UserFactory(role='buyer')
        self.dealer = UserFactory(role='dealer')
        self.currency = CurrencyFactory(code='USD')
        
        # Create test deal with financial data
        self.deal = DealFactory(buyer=self.buyer, dealer=self.dealer)
        self.terms = DealFinancialTermsFactory(
            deal=self.deal,
            currency=self.currency,
            total_price=Decimal('50000')
        )
        
        # Create multiple milestones to test N+1
        for i in range(10):
            PaymentMilestoneFactory(
                deal_financial_terms=self.terms,
                amount_due=Decimal('5000')
            )
        
        # Create financing with installments
        self.financing = FinancingOptionFactory(deal=self.deal)
        
        self.client.force_authenticate(user=self.buyer)
    
    def test_financial_terms_query_count(self):
        """Test query count for financial terms endpoint."""
        url = reverse('deal-financial-terms', kwargs={'pk': self.deal.id})
        
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(url)
        
        query_count = len(context.captured_queries)
        
        print(f"\n[Financial Terms Queries]")
        print(f"  Query count: {query_count}")
        print(f"  Queries:")
        for i, query in enumerate(context.captured_queries, 1):
            print(f"    {i}. {query['sql'][:100]}...")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(
            query_count,
            self.MAX_QUERIES_GET,
            f"Query count {query_count} exceeds maximum {self.MAX_QUERIES_GET}"
        )
    
    def test_payment_schedule_query_count(self):
        """Test query count for payment schedule endpoint (N+1 check)."""
        url = reverse('deal-payment-schedule', kwargs={'pk': self.deal.id})
        
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(url)
        
        query_count = len(context.captured_queries)
        
        print(f"\n[Payment Schedule Queries]")
        print(f"  Query count: {query_count}")
        print(f"  Milestones count: 10")
        print(f"  Queries:")
        for i, query in enumerate(context.captured_queries, 1):
            print(f"    {i}. {query['sql'][:100]}...")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should not have N+1 problem (query count should not scale with milestones)
        self.assertLessEqual(
            query_count,
            self.MAX_QUERIES_GET,
            f"Query count {query_count} exceeds maximum {self.MAX_QUERIES_GET}. Possible N+1 problem."
        )
    
    def test_financing_query_count(self):
        """Test query count for financing endpoint."""
        url = reverse('deal-financing', kwargs={'pk': self.deal.id})
        
        with CaptureQueriesContext(connection) as context:
            response = self.client.get(url)
        
        query_count = len(context.captured_queries)
        
        print(f"\n[Financing Queries]")
        print(f"  Query count: {query_count}")
        print(f"  Queries:")
        for i, query in enumerate(context.captured_queries, 1):
            print(f"    {i}. {query['sql'][:100]}...")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(
            query_count,
            self.MAX_QUERIES_GET,
            f"Query count {query_count} exceeds maximum {self.MAX_QUERIES_GET}"
        )
    
    def test_process_payment_query_count(self):
        """Test query count for process payment endpoint."""
        url = reverse('deal-process-payment', kwargs={'pk': self.deal.id})
        payment_data = {'amount': '5000.00'}
        
        with CaptureQueriesContext(connection) as context:
            response = self.client.post(url, payment_data, format='json')
        
        query_count = len(context.captured_queries)
        
        print(f"\n[Process Payment Queries]")
        print(f"  Query count: {query_count}")
        print(f"  Queries:")
        for i, query in enumerate(context.captured_queries, 1):
            print(f"    {i}. {query['sql'][:100]}...")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(
            query_count,
            self.MAX_QUERIES_POST,
            f"Query count {query_count} exceeds maximum {self.MAX_QUERIES_POST}"
        )


class LoadHandlingTest(TransactionTestCase):
    """Test API performance under concurrent load."""
    
    def setUp(self):
        self.buyer = UserFactory(role='buyer')
        self.dealer = UserFactory(role='dealer')
        self.currency = CurrencyFactory(code='USD')
        
        # Create test deal
        self.deal = DealFactory(buyer=self.buyer, dealer=self.dealer)
        self.terms = DealFinancialTermsFactory(
            deal=self.deal,
            currency=self.currency,
            total_price=Decimal('50000')
        )
        
        for i in range(5):
            PaymentMilestoneFactory(
                deal_financial_terms=self.terms,
                amount_due=Decimal('10000')
            )
    
    def _make_concurrent_requests(self, url, method='GET', data=None, num_requests=10):
        """
        Make concurrent requests and collect statistics.
        
        Returns:
            dict: Statistics about the concurrent requests
        """
        results = {
            'success': 0,
            'failure': 0,
            'times': [],
            'status_codes': []
        }
        
        def make_request():
            client = APIClient()
            client.force_authenticate(user=self.buyer)
            
            start_time = time.perf_counter()
            try:
                if method == 'GET':
                    response = client.get(url)
                elif method == 'POST':
                    response = client.post(url, data, format='json')
                
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                
                return {
                    'success': True,
                    'status_code': response.status_code,
                    'time': elapsed
                }
            except Exception as e:
                end_time = time.perf_counter()
                return {
                    'success': False,
                    'error': str(e),
                    'time': end_time - start_time
                }
        
        # Execute requests concurrently
        with ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            
            for future in as_completed(futures):
                result = future.result()
                if result['success']:
                    results['success'] += 1
                    results['status_codes'].append(result['status_code'])
                else:
                    results['failure'] += 1
                
                results['times'].append(result['time'])
        
        # Calculate statistics
        if results['times']:
            results['mean_time'] = mean(results['times'])
            results['median_time'] = median(results['times'])
            results['min_time'] = min(results['times'])
            results['max_time'] = max(results['times'])
            results['total_time'] = max(results['times'])  # Wall clock time
            results['throughput'] = num_requests / results['total_time']
        
        return results
    
    def test_concurrent_financial_terms_requests(self):
        """Test concurrent GET requests to financial terms endpoint."""
        url = reverse('deal-financial-terms', kwargs={'pk': self.deal.id})
        results = self._make_concurrent_requests(url, method='GET', num_requests=20)
        
        print(f"\n[Concurrent Financial Terms - 20 requests]")
        print(f"  Success: {results['success']}/{results['success'] + results['failure']}")
        print(f"  Mean time: {results['mean_time']*1000:.2f}ms")
        print(f"  Median time: {results['median_time']*1000:.2f}ms")
        print(f"  Min time: {results['min_time']*1000:.2f}ms")
        print(f"  Max time: {results['max_time']*1000:.2f}ms")
        print(f"  Throughput: {results['throughput']:.2f} req/sec")
        
        # At least 90% should succeed
        success_rate = results['success'] / (results['success'] + results['failure'])
        self.assertGreaterEqual(success_rate, 0.9, "Less than 90% success rate under load")
        
        # Throughput should be reasonable (at least 5 req/sec)
        self.assertGreaterEqual(results['throughput'], 5.0, "Throughput below 5 req/sec")
    
    def test_concurrent_payment_schedule_requests(self):
        """Test concurrent GET requests to payment schedule endpoint."""
        url = reverse('deal-payment-schedule', kwargs={'pk': self.deal.id})
        results = self._make_concurrent_requests(url, method='GET', num_requests=20)
        
        print(f"\n[Concurrent Payment Schedule - 20 requests]")
        print(f"  Success: {results['success']}/{results['success'] + results['failure']}")
        print(f"  Mean time: {results['mean_time']*1000:.2f}ms")
        print(f"  Median time: {results['median_time']*1000:.2f}ms")
        print(f"  Throughput: {results['throughput']:.2f} req/sec")
        
        success_rate = results['success'] / (results['success'] + results['failure'])
        self.assertGreaterEqual(success_rate, 0.9, "Less than 90% success rate under load")
        self.assertGreaterEqual(results['throughput'], 5.0, "Throughput below 5 req/sec")
    
    def test_load_test_summary(self):
        """Summary test showing performance across all endpoints."""
        endpoints = [
            ('Financial Terms', reverse('deal-financial-terms', kwargs={'pk': self.deal.id}), 'GET', None),
            ('Payment Schedule', reverse('deal-payment-schedule', kwargs={'pk': self.deal.id}), 'GET', None),
            ('Financing', reverse('deal-financing', kwargs={'pk': self.deal.id}), 'GET', None),
        ]
        
        print(f"\n{'='*70}")
        print(f"LOAD TEST SUMMARY - 10 concurrent requests per endpoint")
        print(f"{'='*70}")
        
        for name, url, method, data in endpoints:
            # Skip financing if not exists
            if 'financing' in url and not hasattr(self.deal, 'financing'):
                FinancingOptionFactory(deal=self.deal)
            
            results = self._make_concurrent_requests(url, method, data, num_requests=10)
            
            success_rate = results['success'] / (results['success'] + results['failure']) * 100
            
            print(f"\n{name}:")
            print(f"  Success Rate: {success_rate:.1f}%")
            print(f"  Mean Time: {results['mean_time']*1000:.2f}ms")
            print(f"  Throughput: {results['throughput']:.2f} req/sec")
            
            self.assertGreaterEqual(success_rate, 90.0, f"{name} success rate below 90%")
        
        print(f"\n{'='*70}\n")
