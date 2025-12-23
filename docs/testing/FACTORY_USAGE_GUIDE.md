# Factory Usage Guide

Complete guide to using test data factories in the Nzila Exports project for creating consistent, realistic test data.

---

## Table of Contents

1. [Overview](#overview)
2. [Available Factories](#available-factories)
3. [Basic Usage](#basic-usage)
4. [Advanced Patterns](#advanced-patterns)
5. [Factory Traits](#factory-traits)
6. [Relationship Management](#relationship-management)
7. [Best Practices](#best-practices)

---

## Overview

### What are Factories?

Factories are a pattern for creating test data objects with sensible defaults, making tests easier to write and maintain. We use the **Factory Boy** library for Python/Django.

### Why Use Factories?

**✅ Benefits:**
- Consistent test data across tests
- Reduced boilerplate code
- Easy to override specific fields
- Automatic handling of relationships
- Realistic data generation with Faker

**❌ Without Factories:**
```python
# Lots of repetitive code
deal = Deal.objects.create(
    deal_number='DEAL-00001',
    buyer=User.objects.create(
        email='buyer@example.com',
        first_name='John',
        last_name='Doe',
        role='buyer'
    ),
    seller=User.objects.create(
        email='seller@example.com',
        first_name='Jane',
        last_name='Smith',
        role='seller'
    ),
    vehicle=Vehicle.objects.create(
        make='Toyota',
        model='Land Cruiser',
        year=2023,
        price=Decimal('45000.00')
    ),
    total_price=Decimal('45000.00'),
    amount_paid=Decimal('0.00'),
    status='pending'
)
```

**✅ With Factories:**
```python
# Clean, simple, consistent
deal = DealFactory()
```

---

## Available Factories

### Core Factories

Located in `tests/factories/`:

#### UserFactory
```python
from tests.factories import UserFactory

# Creates a user with defaults
user = UserFactory()

# Override specific fields
buyer = UserFactory(role='buyer', email='buyer@example.com')
seller = UserFactory(role='seller')
admin = UserFactory(role='admin', is_staff=True)
```

**Default Values:**
- `email`: Unique email (user1@example.com, user2@example.com, ...)
- `first_name`: Random first name (John, Jane, ...)
- `last_name`: Random last name (Doe, Smith, ...)
- `role`: 'buyer'
- `is_active`: True
- `is_verified`: True

#### VehicleFactory
```python
from tests.factories import VehicleFactory

# Create vehicle with defaults
vehicle = VehicleFactory()

# Specific make and model
toyota = VehicleFactory(make='Toyota', model='Land Cruiser')

# With specific price
expensive_car = VehicleFactory(price=Decimal('85000.00'))
```

**Default Values:**
- `make`: Random from ['Toyota', 'Nissan', 'BMW', 'Mercedes', 'Honda']
- `model`: Random model based on make
- `year`: Current year - 1
- `price`: Decimal('45000.00')
- `condition`: 'Good'
- `mileage`: Random between 10,000 and 100,000
- `vin`: Unique VIN number

#### DealFactory
```python
from tests.factories import DealFactory

# Create complete deal with all relationships
deal = DealFactory()

# Customize fields
active_deal = DealFactory(
    status='active',
    total_price=Decimal('50000.00')
)

# With specific buyer and vehicle
deal = DealFactory(
    buyer=UserFactory(email='john@example.com'),
    vehicle=VehicleFactory(make='Toyota')
)
```

**Default Values:**
- `deal_number`: Unique (DEAL-00001, DEAL-00002, ...)
- `buyer`: New UserFactory (role='buyer')
- `seller`: New UserFactory (role='seller')
- `vehicle`: New VehicleFactory
- `total_price`: vehicle.price
- `amount_paid`: Decimal('0.00')
- `status`: 'pending'
- `deal_type`: 'standard'

#### CurrencyFactory
```python
from tests.factories import CurrencyFactory

# Create currency
usd = CurrencyFactory(code='USD', symbol='$')
eur = CurrencyFactory(code='EUR', symbol='€')

# With exchange rate
cad = CurrencyFactory(
    code='CAD',
    symbol='C$',
    exchange_rate_to_usd=Decimal('0.74')
)
```

**Default Values:**
- `code`: 'USD'
- `name`: 'US Dollar'
- `symbol`: '$'
- `exchange_rate_to_usd`: Decimal('1.00')
- `is_active`: True

#### PaymentFactory
```python
from tests.factories import PaymentFactory

# Create payment for a deal
payment = PaymentFactory(
    deal=deal,
    amount=Decimal('5000.00')
)

# With specific status
completed_payment = PaymentFactory(
    deal=deal,
    status='completed',
    payment_method='stripe'
)
```

**Default Values:**
- `deal`: New DealFactory
- `amount`: Decimal('5000.00')
- `status`: 'pending'
- `payment_method`: 'bank_transfer'
- `reference_number`: Unique reference
- `payment_date`: Current date

#### PaymentMilestoneFactory
```python
from tests.factories import PaymentMilestoneFactory

# Create milestone for a deal
milestone = PaymentMilestoneFactory(
    deal=deal,
    name='Initial Deposit',
    amount_due=Decimal('15000.00')
)

# Paid milestone
paid_milestone = PaymentMilestoneFactory(
    deal=deal,
    status='paid',
    paid_amount=Decimal('15000.00')
)
```

**Default Values:**
- `deal`: New DealFactory
- `name`: 'Payment Milestone'
- `amount_due`: Decimal('15000.00')
- `status`: 'pending'
- `due_date`: 30 days from now
- `paid_amount`: Decimal('0.00')

#### FinancingOptionFactory
```python
from tests.factories import FinancingOptionFactory

# Create financing option
financing = FinancingOptionFactory(
    deal=deal,
    interest_rate=Decimal('8.5'),
    term_months=36
)

# Custom terms
custom_financing = FinancingOptionFactory(
    deal=deal,
    interest_rate=Decimal('5.9'),
    term_months=48,
    down_payment=Decimal('10000.00')
)
```

**Default Values:**
- `deal`: New DealFactory
- `interest_rate`: Decimal('8.5')
- `term_months`: 36
- `down_payment`: Decimal('0.00')
- `status`: 'pending'
- `monthly_payment`: Calculated automatically

---

## Basic Usage

### Creating Single Objects

```python
def test_create_single_objects(self):
    """Test creating single objects with factories."""
    # Default values
    user = UserFactory()
    
    # Override specific fields
    buyer = UserFactory(role='buyer')
    
    # Multiple overrides
    admin = UserFactory(
        role='admin',
        email='admin@nzila.com',
        is_staff=True,
        is_superuser=True
    )
    
    # Objects are saved to database
    self.assertIsNotNone(user.id)
    self.assertIsNotNone(buyer.id)
    self.assertIsNotNone(admin.id)
```

### Creating Multiple Objects

```python
def test_create_multiple_objects(self):
    """Test creating multiple objects."""
    # Create 5 users
    users = UserFactory.create_batch(5)
    self.assertEqual(len(users), 5)
    self.assertEqual(User.objects.count(), 5)
    
    # Create 10 deals with specific status
    active_deals = DealFactory.create_batch(
        10,
        status='active'
    )
    self.assertEqual(len(active_deals), 10)
    
    # All have same status
    for deal in active_deals:
        self.assertEqual(deal.status, 'active')
```

### Building Without Saving

```python
def test_build_without_saving(self):
    """Test building objects without saving to database."""
    # Build but don't save
    user = UserFactory.build()
    
    # Not in database
    self.assertIsNone(user.id)
    self.assertEqual(User.objects.count(), 0)
    
    # Can modify before saving
    user.email = 'custom@example.com'
    user.save()
    
    # Now in database
    self.assertIsNotNone(user.id)
    self.assertEqual(User.objects.count(), 1)
```

### Using Sequences

```python
def test_sequences(self):
    """Test that sequences generate unique values."""
    # Create 3 users
    user1 = UserFactory()
    user2 = UserFactory()
    user3 = UserFactory()
    
    # Emails are unique
    self.assertEqual(user1.email, 'user1@example.com')
    self.assertEqual(user2.email, 'user2@example.com')
    self.assertEqual(user3.email, 'user3@example.com')
    
    # Deal numbers are unique
    deal1 = DealFactory()
    deal2 = DealFactory()
    
    self.assertEqual(deal1.deal_number, 'DEAL-00001')
    self.assertEqual(deal2.deal_number, 'DEAL-00002')
```

---

## Advanced Patterns

### Pattern 1: LazyAttribute

Compute field value based on other fields:

```python
class DealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Deal
    
    vehicle = factory.SubFactory(VehicleFactory)
    
    # total_price equals vehicle price
    total_price = factory.LazyAttribute(lambda obj: obj.vehicle.price)
    
    # amount_paid is 33% of total_price
    amount_paid = factory.LazyAttribute(
        lambda obj: obj.total_price * Decimal('0.33')
    )

# Usage
deal = DealFactory()
# total_price automatically set to vehicle.price
# amount_paid automatically set to 33% of total_price
```

### Pattern 2: LazyFunction

Generate field value using a function:

```python
import uuid
from django.utils import timezone

class DealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Deal
    
    # Generate unique reference
    reference = factory.LazyFunction(lambda: uuid.uuid4().hex[:8].upper())
    
    # Use current timestamp
    created_at = factory.LazyFunction(timezone.now)

# Usage
deal1 = DealFactory()  # reference: 'A3F7B2C1'
deal2 = DealFactory()  # reference: '9E4D1F8A' (unique)
```

### Pattern 3: SubFactory

Create related objects automatically:

```python
class DealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Deal
    
    # Automatically create related buyer
    buyer = factory.SubFactory(UserFactory, role='buyer')
    
    # Automatically create related seller
    seller = factory.SubFactory(UserFactory, role='seller')
    
    # Automatically create related vehicle
    vehicle = factory.SubFactory(VehicleFactory)

# Usage
deal = DealFactory()
# Automatically creates: buyer, seller, vehicle
self.assertIsNotNone(deal.buyer.id)
self.assertIsNotNone(deal.seller.id)
self.assertIsNotNone(deal.vehicle.id)

# Can override SubFactory
custom_buyer = UserFactory(email='custom@example.com')
deal = DealFactory(buyer=custom_buyer)
# Uses existing buyer, creates new seller and vehicle
```

### Pattern 4: RelatedFactory

Create reverse relationships:

```python
class DealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Deal
    
    # Create 3 payment milestones automatically
    milestone1 = factory.RelatedFactory(
        PaymentMilestoneFactory,
        factory_related_name='deal',
        name='Initial Deposit'
    )
    milestone2 = factory.RelatedFactory(
        PaymentMilestoneFactory,
        factory_related_name='deal',
        name='Shipping Payment'
    )
    milestone3 = factory.RelatedFactory(
        PaymentMilestoneFactory,
        factory_related_name='deal',
        name='Final Payment'
    )

# Usage
deal = DealFactory()
# Automatically creates 3 milestones
self.assertEqual(deal.paymentmilestone_set.count(), 3)
```

### Pattern 5: PostGeneration

Perform actions after object creation:

```python
class DealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Deal
    
    @factory.post_generation
    def with_payments(self, create, extracted, **kwargs):
        """Add payments after deal creation."""
        if not create:
            return
        
        if extracted:
            # extracted is number of payments to create
            for _ in range(extracted):
                PaymentFactory(deal=self)

# Usage
deal = DealFactory(with_payments=3)
# Creates deal with 3 payments
self.assertEqual(deal.payment_set.count(), 3)
```

---

## Factory Traits

Traits are predefined configurations that can be applied to factories.

### Defining Traits

```python
class DealFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Deal
    
    # Base configuration
    status = 'pending'
    amount_paid = Decimal('0.00')
    
    class Params:
        # Trait for active deal
        active = factory.Trait(
            status='active',
            amount_paid=Decimal('15000.00')
        )
        
        # Trait for completed deal
        completed = factory.Trait(
            status='completed',
            amount_paid=factory.SelfAttribute('total_price')
        )
        
        # Trait for cancelled deal
        cancelled = factory.Trait(
            status='cancelled',
            cancelled_at=factory.LazyFunction(timezone.now),
            cancellation_reason='Test cancellation'
        )
        
        # Trait for financed deal
        financed = factory.Trait(
            has_financing=True,
            financing_approved=True
        )
```

### Using Traits

```python
def test_using_traits(self):
    """Test using factory traits."""
    # Active deal
    active_deal = DealFactory(active=True)
    self.assertEqual(active_deal.status, 'active')
    self.assertEqual(active_deal.amount_paid, Decimal('15000.00'))
    
    # Completed deal
    completed_deal = DealFactory(completed=True)
    self.assertEqual(completed_deal.status, 'completed')
    self.assertEqual(completed_deal.amount_paid, completed_deal.total_price)
    
    # Cancelled deal
    cancelled_deal = DealFactory(cancelled=True)
    self.assertEqual(cancelled_deal.status, 'cancelled')
    self.assertIsNotNone(cancelled_deal.cancelled_at)
    
    # Combine traits
    financed_active_deal = DealFactory(active=True, financed=True)
    self.assertEqual(financed_active_deal.status, 'active')
    self.assertTrue(financed_active_deal.has_financing)
```

### Common Trait Patterns

```python
class VehicleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vehicle
    
    class Params:
        # Condition traits
        excellent = factory.Trait(
            condition='Excellent',
            mileage=15000,
            price=Decimal('55000.00')
        )
        
        good = factory.Trait(
            condition='Good',
            mileage=50000,
            price=Decimal('45000.00')
        )
        
        fair = factory.Trait(
            condition='Fair',
            mileage=100000,
            price=Decimal('35000.00')
        )
        
        # Make traits
        toyota = factory.Trait(
            make='Toyota',
            model='Land Cruiser'
        )
        
        nissan = factory.Trait(
            make='Nissan',
            model='Patrol'
        )

# Usage
excellent_toyota = VehicleFactory(excellent=True, toyota=True)
fair_nissan = VehicleFactory(fair=True, nissan=True)
```

---

## Relationship Management

### One-to-Many Relationships

```python
def test_one_to_many(self):
    """Test one-to-many relationships."""
    # Create deal
    deal = DealFactory()
    
    # Add multiple payments
    payment1 = PaymentFactory(deal=deal, amount=Decimal('5000.00'))
    payment2 = PaymentFactory(deal=deal, amount=Decimal('7000.00'))
    payment3 = PaymentFactory(deal=deal, amount=Decimal('3000.00'))
    
    # Verify relationship
    self.assertEqual(deal.payment_set.count(), 3)
    self.assertEqual(
        sum(p.amount for p in deal.payment_set.all()),
        Decimal('15000.00')
    )
```

### Many-to-Many Relationships

```python
class VehicleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Vehicle
    
    @factory.post_generation
    def features(self, create, extracted, **kwargs):
        """Add features to vehicle."""
        if not create:
            return
        
        if extracted:
            # extracted is a list of features
            for feature in extracted:
                self.features.add(feature)

# Usage
def test_many_to_many(self):
    """Test many-to-many relationships."""
    # Create features
    leather = FeatureFactory(name='Leather Seats')
    sunroof = FeatureFactory(name='Sunroof')
    nav = FeatureFactory(name='Navigation')
    
    # Create vehicle with features
    vehicle = VehicleFactory(features=[leather, sunroof, nav])
    
    # Verify
    self.assertEqual(vehicle.features.count(), 3)
    self.assertIn(leather, vehicle.features.all())
```

### Nested Relationships

```python
def test_nested_relationships(self):
    """Test creating nested relationships."""
    # Create deal with full relationship tree
    deal = DealFactory(
        # Buyer with profile
        buyer=UserFactory(
            email='buyer@example.com',
            profile__country='US',
            profile__phone='+1234567890'
        ),
        # Vehicle with features
        vehicle=VehicleFactory(
            make='Toyota',
            model='Land Cruiser',
            features=[
                FeatureFactory(name='4WD'),
                FeatureFactory(name='Leather')
            ]
        )
    )
    
    # Create related objects
    PaymentFactory(deal=deal, amount=Decimal('15000.00'))
    PaymentMilestoneFactory(deal=deal, name='Deposit')
    FinancingOptionFactory(deal=deal, term_months=36)
    
    # Verify all relationships
    self.assertEqual(deal.buyer.email, 'buyer@example.com')
    self.assertEqual(deal.buyer.profile.country, 'US')
    self.assertEqual(deal.vehicle.make, 'Toyota')
    self.assertEqual(deal.vehicle.features.count(), 2)
    self.assertEqual(deal.payment_set.count(), 1)
    self.assertEqual(deal.paymentmilestone_set.count(), 1)
    self.assertIsNotNone(deal.financing)
```

---

## Best Practices

### ✅ DO

1. **Use factories for all test data**
```python
# ✅ GOOD
deal = DealFactory()

# ❌ BAD
deal = Deal.objects.create(
    deal_number='DEAL-001',
    buyer=User.objects.create(...),
    # ... lots of boilerplate
)
```

2. **Override only what you need**
```python
# ✅ GOOD - Override only status
deal = DealFactory(status='active')

# ❌ BAD - Overriding everything unnecessarily
deal = DealFactory(
    status='active',
    deal_number='DEAL-001',  # Unnecessary
    buyer=UserFactory(),      # Unnecessary
    # ...
)
```

3. **Use traits for common configurations**
```python
# ✅ GOOD
completed_deal = DealFactory(completed=True)

# ❌ BAD
completed_deal = DealFactory(
    status='completed',
    amount_paid=Decimal('45000.00'),
    completed_at=timezone.now()
)
```

4. **Create factories for all models**
```python
# Create a factory for every model you test
# Even simple models benefit from factories
```

5. **Use realistic data with Faker**
```python
import factory.faker

class UserFactory(factory.django.DjangoModelFactory):
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
```

### ❌ DON'T

1. **Don't create objects manually**
```python
# ❌ BAD
user = User.objects.create(email='test@example.com', ...)
```

2. **Don't hardcode IDs**
```python
# ❌ BAD
deal = Deal.objects.get(id=1)

# ✅ GOOD
deal = DealFactory()
```

3. **Don't create factories in test files**
```python
# ❌ BAD - Factory in test file
class MyTest(TestCase):
    def create_user(self):
        return User.objects.create(...)

# ✅ GOOD - Use factory from factories module
from tests.factories import UserFactory

class MyTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
```

4. **Don't share factory instances between tests**
```python
# ❌ BAD
class MyTest(TestCase):
    user = UserFactory()  # Shared!
    
    def test_one(self):
        self.user.email = 'new@example.com'
    
    def test_two(self):
        # user.email might be 'new@example.com' from test_one!
        pass

# ✅ GOOD
class MyTest(TestCase):
    def setUp(self):
        self.user = UserFactory()  # Fresh for each test
```

5. **Don't build complex object graphs manually**
```python
# ❌ BAD
buyer = User.objects.create(...)
seller = User.objects.create(...)
vehicle = Vehicle.objects.create(...)
deal = Deal.objects.create(buyer=buyer, seller=seller, vehicle=vehicle, ...)

# ✅ GOOD
deal = DealFactory()  # Creates everything automatically
```

---

## Quick Reference

### Most Common Factory Operations

```python
# Create single object
obj = MyFactory()

# Create with overrides
obj = MyFactory(field='value')

# Create multiple objects
objs = MyFactory.create_batch(5)

# Build without saving
obj = MyFactory.build()

# Use traits
obj = MyFactory(trait_name=True)

# Create with related objects
obj = MyFactory(
    related_field=RelatedFactory(),
    related_field__nested_field='value'
)
```

### When to Use Each Factory

| Factory | Use When |
|---------|----------|
| `UserFactory` | Need buyer, seller, or admin users |
| `VehicleFactory` | Need vehicles for deals |
| `DealFactory` | Need deals (creates buyer, seller, vehicle) |
| `PaymentFactory` | Need payment records |
| `PaymentMilestoneFactory` | Need payment schedule milestones |
| `FinancingOptionFactory` | Need financing terms |
| `CurrencyFactory` | Need currency conversion testing |

---

**Last Updated**: December 20, 2024  
**Version**: 1.0
