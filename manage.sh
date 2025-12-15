#!/bin/bash
# Nzila Export Hub - Development Helper Script

echo "==================================="
echo "Nzila Export Hub - Helper Script"
echo "==================================="
echo ""

# Function to display menu
show_menu() {
    echo "Available commands:"
    echo "1. Run development server"
    echo "2. Create superuser"
    echo "3. Make migrations"
    echo "4. Apply migrations"
    echo "5. Run tests"
    echo "6. Check for stalled leads/deals"
    echo "7. Collect static files"
    echo "8. Create sample data"
    echo "9. Exit"
    echo ""
}

# Function to create sample data
create_sample_data() {
    python manage.py shell << EOF
from django.contrib.auth import get_user_model
from vehicles.models import Vehicle
from deals.models import Lead, Deal
from decimal import Decimal

User = get_user_model()

# Create users if they don't exist
admin, _ = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@nzila.com',
        'role': 'admin',
        'is_staff': True,
        'is_superuser': True
    }
)
if _:
    admin.set_password('admin123')
    admin.save()
    print(f"Created admin user: {admin.username}")

dealer, _ = User.objects.get_or_create(
    username='dealer1',
    defaults={
        'email': 'dealer@nzila.com',
        'role': 'dealer',
        'company_name': 'Toronto Auto Exports'
    }
)
if _:
    dealer.set_password('dealer123')
    dealer.save()
    print(f"Created dealer user: {dealer.username}")

buyer, _ = User.objects.get_or_create(
    username='buyer1',
    defaults={
        'email': 'buyer@nzila.com',
        'role': 'buyer',
        'company_name': 'West African Imports',
        'country': 'Senegal'
    }
)
if _:
    buyer.set_password('buyer123')
    buyer.save()
    print(f"Created buyer user: {buyer.username}")

broker, _ = User.objects.get_or_create(
    username='broker1',
    defaults={
        'email': 'broker@nzila.com',
        'role': 'broker',
        'company_name': 'Auto Export Brokers'
    }
)
if _:
    broker.set_password('broker123')
    broker.save()
    print(f"Created broker user: {broker.username}")

# Create sample vehicles
if not Vehicle.objects.filter(dealer=dealer).exists():
    vehicles_data = [
        {
            'make': 'Toyota',
            'model': 'Camry',
            'year': 2020,
            'vin': '1HGBH41JXMN109186',
            'condition': 'used_good',
            'mileage': 50000,
            'color': 'Blue',
            'price_cad': Decimal('25000.00'),
            'location': 'Toronto, ON'
        },
        {
            'make': 'Honda',
            'model': 'Accord',
            'year': 2019,
            'vin': '1HGCM82633A123456',
            'condition': 'used_excellent',
            'mileage': 30000,
            'color': 'Black',
            'price_cad': Decimal('28000.00'),
            'location': 'Montreal, QC'
        },
        {
            'make': 'Ford',
            'model': 'F-150',
            'year': 2021,
            'vin': '1FTFW1E54MFA12345',
            'condition': 'used_good',
            'mileage': 45000,
            'color': 'White',
            'price_cad': Decimal('35000.00'),
            'location': 'Vancouver, BC'
        }
    ]
    
    for veh_data in vehicles_data:
        vehicle = Vehicle.objects.create(dealer=dealer, **veh_data)
        print(f"Created vehicle: {vehicle}")

print("")
print("Sample data created successfully!")
print("")
print("Login credentials:")
print("  Admin: admin / admin123")
print("  Dealer: dealer1 / dealer123")
print("  Buyer: buyer1 / buyer123")
print("  Broker: broker1 / broker123")
EOF
}

# Main script loop
while true; do
    show_menu
    read -p "Enter your choice [1-9]: " choice
    
    case $choice in
        1)
            echo "Starting development server..."
            python manage.py runserver
            ;;
        2)
            echo "Creating superuser..."
            python manage.py createsuperuser
            ;;
        3)
            echo "Making migrations..."
            python manage.py makemigrations
            ;;
        4)
            echo "Applying migrations..."
            python manage.py migrate
            ;;
        5)
            echo "Running tests..."
            python manage.py test
            ;;
        6)
            echo "Checking for stalled leads and deals..."
            python manage.py check_stalled
            ;;
        7)
            echo "Collecting static files..."
            python manage.py collectstatic --noinput
            ;;
        8)
            echo "Creating sample data..."
            create_sample_data
            ;;
        9)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid option. Please try again."
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
    clear
done
