"""
Base test classes for Nzila E-Exports test suite.

Provides reusable base classes with common setup and helper methods
to reduce code duplication and improve test maintainability.
"""

from django.test import TestCase
from rest_framework.test import APIClient

from tests.factories import (
    UserFactory,
    DealFactory,
    DealFinancialTermsFactory,
    PaymentMilestoneFactory,
    FinancingOptionFactory,
    VehicleFactory
)


class BaseAPITestCase(TestCase):
    """
    Base class for API tests with common setup and authentication helpers.
    
    Provides:
    - Pre-configured API client
    - Common user roles (buyer, dealer, other_user)
    - Authentication helper methods
    - Authenticated request helpers
    """
    
    def setUp(self):
        """Set up common test fixtures."""
        self.client = APIClient()
        self.buyer = UserFactory(role='buyer')
        self.dealer = UserFactory(role='dealer')
        self.other_user = UserFactory(role='buyer')
    
    def authenticate(self, user=None):
        """
        Authenticate client as specified user.
        
        Args:
            user: User to authenticate as. Defaults to self.buyer.
        """
        user = user or self.buyer
        self.client.force_authenticate(user=user)
    
    def get_authenticated(self, url, user=None, **kwargs):
        """
        Make authenticated GET request.
        
        Args:
            url: URL to request
            user: User to authenticate as. Defaults to self.buyer.
            **kwargs: Additional arguments to pass to client.get()
        
        Returns:
            Response object
        """
        self.authenticate(user)
        return self.client.get(url, **kwargs)
    
    def post_authenticated(self, url, data=None, user=None, **kwargs):
        """
        Make authenticated POST request.
        
        Args:
            url: URL to request
            data: Request data
            user: User to authenticate as. Defaults to self.buyer.
            **kwargs: Additional arguments to pass to client.post()
        
        Returns:
            Response object
        """
        self.authenticate(user)
        return self.client.post(url, data, format='json', **kwargs)
    
    def put_authenticated(self, url, data=None, user=None, **kwargs):
        """
        Make authenticated PUT request.
        
        Args:
            url: URL to request
            data: Request data
            user: User to authenticate as. Defaults to self.buyer.
            **kwargs: Additional arguments to pass to client.put()
        
        Returns:
            Response object
        """
        self.authenticate(user)
        return self.client.put(url, data, format='json', **kwargs)
    
    def patch_authenticated(self, url, data=None, user=None, **kwargs):
        """
        Make authenticated PATCH request.
        
        Args:
            url: URL to request
            data: Request data
            user: User to authenticate as. Defaults to self.buyer.
            **kwargs: Additional arguments to pass to client.patch()
        
        Returns:
            Response object
        """
        self.authenticate(user)
        return self.client.patch(url, data, format='json', **kwargs)
    
    def delete_authenticated(self, url, user=None, **kwargs):
        """
        Make authenticated DELETE request.
        
        Args:
            url: URL to request
            user: User to authenticate as. Defaults to self.buyer.
            **kwargs: Additional arguments to pass to client.delete()
        
        Returns:
            Response object
        """
        self.authenticate(user)
        return self.client.delete(url, **kwargs)


class BaseFinancialAPITestCase(BaseAPITestCase):
    """
    Base class for financial API tests.
    
    Extends BaseAPITestCase with financial-specific fixtures:
    - Deal with buyer and dealer
    - Financial terms for the deal
    - Helper methods for creating payment schedules and financing
    """
    
    def setUp(self):
        """Set up common financial test fixtures."""
        super().setUp()
        self.vehicle = VehicleFactory()
        self.deal = DealFactory(
            buyer=self.buyer,
            dealer=self.dealer,
            vehicle=self.vehicle,
            status='active'
        )
        self.terms = DealFinancialTermsFactory(deal=self.deal)
    
    def create_payment_schedule(self, num_milestones=3, **kwargs):
        """
        Create payment schedule for the deal.
        
        Args:
            num_milestones: Number of payment milestones to create
            **kwargs: Additional arguments to pass to PaymentMilestoneFactory
        
        Returns:
            List of created PaymentMilestone instances
        """
        return PaymentMilestoneFactory.create_batch(
            num_milestones,
            deal_financial_terms=self.terms,
            **kwargs
        )
    
    def create_financing(self, **kwargs):
        """
        Create financing option for the deal.
        
        Args:
            **kwargs: Additional arguments to pass to FinancingOptionFactory
        
        Returns:
            Created FinancingOption instance
        """
        return FinancingOptionFactory(
            deal=self.deal,
            **kwargs
        )
    
    def create_deal_with_schedule(self, num_milestones=3):
        """
        Create a complete deal with financial terms and payment schedule.
        
        Args:
            num_milestones: Number of payment milestones to create
        
        Returns:
            Tuple of (deal, terms, milestones)
        """
        milestones = self.create_payment_schedule(num_milestones)
        return self.deal, self.terms, milestones
    
    def create_deal_with_financing(self, num_installments=0):
        """
        Create a complete deal with financial terms and financing.
        
        Args:
            num_installments: Number of financing installments to create
        
        Returns:
            Tuple of (deal, terms, financing, installments)
        """
        financing = self.create_financing()
        installments = []
        
        if num_installments > 0:
            from tests.factories import FinancingInstallmentFactory
            installments = FinancingInstallmentFactory.create_batch(
                num_installments,
                financing=financing
            )
        
        return self.deal, self.terms, financing, installments


class BasePerformanceTestCase(BaseFinancialAPITestCase):
    """
    Base class for performance tests.
    
    Extends BaseFinancialAPITestCase with performance-specific helpers:
    - Bulk data creation
    - Performance assertion helpers
    - Query count tracking
    """
    
    def create_bulk_deals(self, count=10):
        """
        Create multiple deals for performance testing.
        
        Args:
            count: Number of deals to create
        
        Returns:
            List of created Deal instances
        """
        deals = []
        for _ in range(count):
            deal = DealFactory(buyer=self.buyer, dealer=self.dealer)
            DealFinancialTermsFactory(deal=deal)
            deals.append(deal)
        return deals
    
    def create_bulk_payment_schedules(self, num_deals=10, milestones_per_deal=3):
        """
        Create payment schedules for multiple deals.
        
        Args:
            num_deals: Number of deals to create
            milestones_per_deal: Number of milestones per deal
        
        Returns:
            List of created Deal instances with payment schedules
        """
        deals = self.create_bulk_deals(num_deals)
        for deal in deals:
            terms = deal.deal_financial_terms
            PaymentMilestoneFactory.create_batch(
                milestones_per_deal,
                deal_financial_terms=terms
            )
        return deals
    
    def assertResponseTime(self, response, max_ms):
        """
        Assert that response was generated within specified time.
        
        Args:
            response: Response object (must have _request_time attribute)
            max_ms: Maximum allowed response time in milliseconds
        """
        if hasattr(response, '_request_time'):
            actual_ms = response._request_time * 1000
            self.assertLess(
                actual_ms,
                max_ms,
                f"Response took {actual_ms:.2f}ms, expected less than {max_ms}ms"
            )
    
    def assertMaxQueries(self, num_queries):
        """
        Context manager to assert maximum number of database queries.
        
        Args:
            num_queries: Maximum allowed number of queries
        
        Returns:
            Context manager for assertNumQueries
        """
        return self.assertNumQueries(num_queries)
