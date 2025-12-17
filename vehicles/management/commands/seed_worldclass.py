"""
World-class data seeding for Nzila Export Hub
Creates comprehensive, realistic test data for all models
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with world-class comprehensive test data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🌍 Starting world-class data seeding...'))
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        self.stdout.write('Clearing existing data...')
        from vehicles.models import Vehicle, VehicleImage, Offer
        from deals.models import Deal
        from commissions.models import Commission
        from chat.models import Conversation, Message
        from notifications.models import Notification
        
        # Clear in correct order to respect foreign keys
        Message.objects.all().delete()
        Conversation.objects.all().delete()
        Notification.objects.all().delete()
        Commission.objects.all().delete()
        Offer.objects.all().delete()
        Deal.objects.all().delete()
        VehicleImage.objects.all().delete()
        Vehicle.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        
        # Create users
        self.stdout.write('Creating users...')
        admin = self.create_admin()
        dealers = self.create_dealers()
        brokers = self.create_brokers()
        buyers = self.create_buyers()
        
        # Create vehicles
        self.stdout.write('Creating vehicles...')
        vehicles = self.create_vehicles(dealers)
        
        # Create deals
        self.stdout.write('Creating deals...')
        deals = self.create_deals(vehicles, buyers, brokers)
        
        # Create commissions
        self.stdout.write('Creating commissions...')
        self.create_commissions(deals, brokers)
        
        # Create offers
        self.stdout.write('Creating offers...')
        self.create_offers(vehicles, buyers)
        
        # Create conversations
        self.stdout.write('Creating conversations...')
        self.create_conversations(buyers, dealers, vehicles)
        
        # Create notifications
        self.stdout.write('Creating notifications...')
        self.create_notifications(buyers, dealers, brokers)
        
        self.stdout.write(self.style.SUCCESS('✅ World-class seeding completed!'))
        self.print_summary(admin, dealers, brokers, buyers, vehicles, deals)
    
    def create_admin(self):
        admin, created = User.objects.get_or_create(
            email='admin@nzila.com',
            defaults={
                'username': 'admin',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': 'admin',
                'phone': '+1-416-555-0001',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(f'  ✓ Admin: {admin.email}')
        return admin
    
    def create_dealers(self):
        dealers_data = [
            {'first': 'Michael', 'last': 'Thompson', 'company': 'Premium Auto Exports', 'city': 'Toronto'},
            {'first': 'Sarah', 'last': 'Johnson', 'company': 'Elite Motors Canada', 'city': 'Vancouver'},
            {'first': 'David', 'last': 'Chen', 'company': 'Global Auto Trading', 'city': 'Montreal'},
            {'first': 'Jennifer', 'last': 'Williams', 'company': 'Atlantic Vehicle Export', 'city': 'Halifax'},
            {'first': 'Robert', 'last': 'Anderson', 'company': 'Canadian Auto Direct', 'city': 'Calgary'},
        ]
        
        dealers = []
        for i, data in enumerate(dealers_data, 1):
            dealer, created = User.objects.get_or_create(
                email=f"{data['first'].lower()}.{data['last'].lower()}@dealer.com",
                defaults={
                    'username': f"dealer_{data['first'].lower()}",
                    'first_name': data['first'],
                    'last_name': data['last'],
                    'role': 'dealer',
                    'phone': f'+1-416-555-{1000+i:04d}',
                    'company_name': data['company'],
                    'address': f'{100+i*10} Export Ave, {data["city"]}, Canada',
                }
            )
            if created:
                dealer.set_password('dealer123')
                dealer.save()
                self.stdout.write(f'  ✓ Dealer: {dealer.email} - {data["company"]}')
            dealers.append(dealer)
        
        return dealers
    
    def create_brokers(self):
        brokers_data = [
            {'first': 'Amadou', 'last': 'Diallo', 'country': 'Senegal', 'city': 'Dakar'},
            {'first': 'Fatima', 'last': 'Koné', 'country': 'Côte d\'Ivoire', 'city': 'Abidjan'},
            {'first': 'Ibrahim', 'last': 'Nwosu', 'country': 'Nigeria', 'city': 'Lagos'},
            {'first': 'Amina', 'last': 'Mensah', 'country': 'Ghana', 'city': 'Accra'},
            {'first': 'Omar', 'last': 'Ba', 'country': 'Senegal', 'city': 'Dakar'},
        ]
        
        brokers = []
        for i, data in enumerate(brokers_data, 1):
            broker, created = User.objects.get_or_create(
                email=f"{data['first'].lower()}.{data['last'].lower()}@broker.com",
                defaults={
                    'username': f"broker_{data['first'].lower()}",
                    'first_name': data['first'],
                    'last_name': data['last'],
                    'role': 'broker',
                    'phone': f'+221-77-{100+i:03d}-{1000+i:04d}',
                    'company_name': f'{data["first"]} Auto Imports',
                    'address': f'{data["city"]}, {data["country"]}',
                }
            )
            if created:
                broker.set_password('broker123')
                broker.save()
                self.stdout.write(f'  ✓ Broker: {broker.email} - {data["city"]}')
            brokers.append(broker)
        
        return brokers
    
    def create_buyers(self):
        buyers_data = [
            {'first': 'Moussa', 'last': 'Traoré', 'country': 'Mali', 'city': 'Bamako'},
            {'first': 'Aisha', 'last': 'Kamara', 'country': 'Sierra Leone', 'city': 'Freetown'},
            {'first': 'Kwame', 'last': 'Osei', 'country': 'Ghana', 'city': 'Kumasi'},
            {'first': 'Zainab', 'last': 'Musa', 'country': 'Nigeria', 'city': 'Kano'},
            {'first': 'Jean', 'last': 'Kabongo', 'country': 'DR Congo', 'city': 'Kinshasa'},
            {'first': 'Marie', 'last': 'Ndong', 'country': 'Cameroon', 'city': 'Douala'},
            {'first': 'Ahmed', 'last': 'Hassan', 'country': 'Egypt', 'city': 'Cairo'},
            {'first': 'Fatou', 'last': 'Sall', 'country': 'Senegal', 'city': 'Thies'},
        ]
        
        buyers = []
        for i, data in enumerate(buyers_data, 1):
            buyer, created = User.objects.get_or_create(
                email=f"{data['first'].lower()}.{data['last'].lower()}@buyer.com",
                defaults={
                    'username': f"buyer_{data['first'].lower()}",
                    'first_name': data['first'],
                    'last_name': data['last'],
                    'role': 'buyer',
                    'phone': f'+{220+i}-{70+i}-{100+i:03d}-{2000+i:04d}',
                    'address': f'{data["city"]}, {data["country"]}',
                }
            )
            if created:
                buyer.set_password('buyer123')
                buyer.save()
                self.stdout.write(f'  ✓ Buyer: {buyer.email} - {data["city"]}')
            buyers.append(buyer)
        
        return buyers
    
    def create_vehicles(self, dealers):
        from vehicles.models import Vehicle
        
        vehicles_data = [
            # Luxury Sedans
            {'make': 'BMW', 'model': '5 Series', 'year': 2021, 'price': 35000, 'mileage': 45000, 'color': 'Black', 'condition': 'used_excellent', 'transmission': 'Automatic', 'fuel': 'Gasoline'},
            {'make': 'Mercedes-Benz', 'model': 'E-Class', 'year': 2020, 'price': 38000, 'mileage': 52000, 'color': 'Silver', 'condition': 'used_excellent', 'transmission': 'Automatic', 'fuel': 'Gasoline'},
            {'make': 'Audi', 'model': 'A6', 'year': 2021, 'price': 36000, 'mileage': 38000, 'color': 'White', 'condition': 'used_excellent', 'transmission': 'Automatic', 'fuel': 'Gasoline'},
            {'make': 'Lexus', 'model': 'ES 350', 'year': 2019, 'price': 32000, 'mileage': 55000, 'color': 'Gray', 'condition': 'used_good', 'transmission': 'Automatic', 'fuel': 'Gasoline'},
            
            # SUVs
            {'make': 'Toyota', 'model': 'RAV4', 'year': 2022, 'price': 28000, 'mileage': 25000, 'color': 'Blue', 'condition': 'new', 'transmission': 'Automatic', 'fuel': 'Gasoline'},
            {'make': 'Honda', 'model': 'CR-V', 'year': 2021, 'price': 27000, 'mileage': 35000, 'color': 'Red', 'condition': 'used_excellent', 'transmission': 'Automatic', 'fuel': 'Gasoline'},
            {'make': 'Nissan', 'model': 'Rogue', 'year': 2020, 'price': 24000, 'mileage': 48000, 'color': 'Black', 'condition': 'used_good', 'transmission': 'Automatic', 'fuel': 'Gasoline'},
            {'make': 'Mazda', 'model': 'CX-5', 'year': 2021, 'price': 26000, 'mileage': 32000, 'color': 'White', 'condition': 'used_excellent', 'transmission': 'Automatic', 'fuel': 'Gasoline'},
            {'make': 'Hyundai', 'model': 'Tucson', 'year': 2022, 'price': 25000, 'mileage': 28000, 'color': 'Gray', 'condition': 'new', 'transmission': 'Automatic', 'fuel': 'Gasoline'},
            
            # Trucks
            {'make': 'Ford', 'model': 'F-150', 'year': 2020, 'price': 32000, 'mileage': 55000, 'color': 'Black', 'condition': 'used_good', 'transmission': 'Automatic', 'fuel': 'Gasoline'},
            {'make': 'Chevrolet', 'model': 'Silverado', 'year': 2021, 'price': 34000, 'mileage': 42000, 'color': 'Red', 'condition': 'used_excellent', 'transmission': 'Automatic', 'fuel': 'Gasoline'},
            {'make': 'RAM', 'model': '1500', 'year': 2020, 'price': 33000, 'mileage': 48000, 'color': 'White', 'condition': 'used_fair', 'transmission': 'Automatic', 'fuel': 'Diesel'},
            
            # Sedans
            {'make': 'Toyota', 'model': 'Camry', 'year': 2021, 'price': 22000, 'mileage': 38000, 'color': 'Silver', 'condition': 'used_excellent', 'transmission': 'Automatic', 'fuel': 'Gasoline'},
            {'make': 'Honda', 'model': 'Accord', 'year': 2020, 'price': 21000, 'mileage': 45000, 'color': 'Blue', 'condition': 'used_good', 'transmission': 'Automatic', 'fuel': 'Gasoline'},
            {'make': 'Nissan', 'model': 'Altima', 'year': 2021, 'price': 20000, 'mileage': 35000, 'color': 'Black', 'condition': 'used_excellent', 'transmission': 'Automatic', 'fuel': 'Gasoline'},
            {'make': 'Hyundai', 'model': 'Sonata', 'year': 2020, 'price': 19000, 'mileage': 42000, 'color': 'White', 'condition': 'used_good', 'transmission': 'Automatic', 'fuel': 'Gasoline'},
            
            # Compact Cars
            {'make': 'Toyota', 'model': 'Corolla', 'year': 2021, 'price': 18000, 'mileage': 32000, 'color': 'Red', 'condition': 'used_excellent', 'transmission': 'Automatic', 'fuel': 'Gasoline'},
            {'make': 'Honda', 'model': 'Civic', 'year': 2020, 'price': 17000, 'mileage': 38000, 'color': 'Gray', 'condition': 'used_fair', 'transmission': 'Automatic', 'fuel': 'Gasoline'},
            {'make': 'Mazda', 'model': '3', 'year': 2021, 'price': 17500, 'mileage': 28000, 'color': 'Blue', 'condition': 'new', 'transmission': 'Automatic', 'fuel': 'Gasoline'},
            {'make': 'Volkswagen', 'model': 'Jetta', 'year': 2020, 'price': 16500, 'mileage': 45000, 'color': 'Black', 'condition': 'used_good', 'transmission': 'Automatic', 'fuel': 'Gasoline'},
        ]
        
        vehicles = []
        locations = ['Toronto, ON', 'Vancouver, BC', 'Montreal, QC', 'Calgary, AB', 'Halifax, NS']
        
        for i, vdata in enumerate(vehicles_data):
            dealer = dealers[i % len(dealers)]
            
            vehicle = Vehicle.objects.create(
                dealer=dealer,
                make=vdata['make'],
                model=vdata['model'],
                year=vdata['year'],
                vin=f'1HGBH41JXMN{100000+i:06d}',
                condition=vdata['condition'],
                mileage=vdata['mileage'],
                color=vdata['color'],
                fuel_type=vdata['fuel'],
                transmission=vdata['transmission'],
                price_cad=Decimal(str(vdata['price'])),
                location=locations[i % len(locations)],
                status=random.choice(['available', 'available', 'available', 'reserved', 'sold']),
                description=f"Excellent {vdata['year']} {vdata['make']} {vdata['model']} in {vdata['color']}. Well-maintained, clean title, ready for export. Perfect for African markets.",
            )
            
            vehicles.append(vehicle)
            
            if (i + 1) % 5 == 0:
                self.stdout.write(f'  ✓ Created {i+1} vehicles')
        
        self.stdout.write(f'  ✓ Total vehicles created: {len(vehicles)}')
        return vehicles
    
    def create_deals(self, vehicles, buyers, brokers):
        from deals.models import Deal
        
        deals = []
        statuses = ['pending_docs', 'docs_verified', 'payment_pending', 'payment_received', 'ready_to_ship', 'shipped', 'completed', 'cancelled']
        
        # Create 15 deals with various statuses
        for i in range(15):
            vehicle = vehicles[i]
            buyer = buyers[i % len(buyers)]
            dealer = vehicle.dealer
            broker = brokers[i % len(brokers)] if i % 3 == 0 else None  # Some deals have brokers
            
            status = statuses[i % len(statuses)]
            
            deal = Deal.objects.create(
                vehicle=vehicle,
                buyer=buyer,
                dealer=dealer,
                broker=broker,
                status=status,
                agreed_price_cad=vehicle.price_cad,
                notes=f'Deal for {vehicle.year} {vehicle.make} {vehicle.model}',
            )
            
            # Mark completed if status is completed
            if status == 'completed':
                deal.completed_at = timezone.now() - timedelta(days=random.randint(1, 30))
                deal.save()
            
            deals.append(deal)
        
        self.stdout.write(f'  ✓ Created {len(deals)} deals')
        return deals
    
    def create_commissions(self, deals, brokers):
        from commissions.models import Commission
        
        commissions = []
        for deal in deals:
            if deal.broker:
                rate = Decimal('5.00')  # 5% commission
                amount = deal.agreed_price_cad * Decimal('0.05')
                
                commission = Commission.objects.create(
                    deal=deal,
                    recipient=deal.broker,
                    commission_type='broker',
                    percentage=rate,
                    amount_cad=amount,
                    status='paid' if deal.status == 'completed' else 'pending',
                    notes=f'Broker commission for {deal.vehicle.make} {deal.vehicle.model}',
                )
                
                commissions.append(commission)
        
        self.stdout.write(f'  ✓ Created {len(commissions)} commissions')
        return commissions
    
    def create_offers(self, vehicles, buyers):
        from vehicles.models import Offer
        
        offers = []
        statuses = ['pending', 'accepted', 'rejected', 'countered', 'withdrawn']
        
        # Create 20 offers
        for i in range(20):
            vehicle = vehicles[i % len(vehicles)]
            buyer = buyers[i % len(buyers)]
            status = statuses[i % len(statuses)]
            
            offer_amount = vehicle.price_cad * Decimal(str(random.uniform(0.85, 0.98)))
            
            offer = Offer.objects.create(
                vehicle=vehicle,
                buyer=buyer,
                offer_amount_cad=offer_amount,
                message=f'Interested in this {vehicle.year} {vehicle.make} {vehicle.model}. Is this price negotiable?',
                status=status,
                valid_until=timezone.now() + timedelta(days=7),
            )
            
            # Add counter offers for countered status
            if status == 'countered':
                offer.counter_amount_cad = vehicle.price_cad * Decimal('0.95')
                offer.counter_message = 'We can meet you at this price. This is our best offer.'
                offer.responded_at = timezone.now() - timedelta(hours=random.randint(1, 48))
                offer.save()
            
            # Add dealer notes for accepted/rejected
            if status in ['accepted', 'rejected']:
                offer.responded_at = timezone.now() - timedelta(hours=random.randint(1, 72))
                if status == 'accepted':
                    offer.dealer_notes = 'Offer accepted. Please proceed with payment.'
                else:
                    offer.dealer_notes = 'Unfortunately, we cannot accept this offer at this time.'
                offer.save()
            
            offers.append(offer)
        
        self.stdout.write(f'  ✓ Created {len(offers)} offers')
        return offers
    
    def create_conversations(self, buyers, dealers, vehicles):
        from chat.models import Conversation, Message
        
        conversations = []
        
        # Create 10 conversations
        for i in range(10):
            buyer = buyers[i % len(buyers)]
            dealer = dealers[i % len(dealers)]
            vehicle = vehicles[i % len(vehicles)]
            
            conversation = Conversation.objects.create(
                participant_1=buyer,
                participant_2=dealer,
                vehicle=vehicle,
                subject=f'Inquiry about {vehicle.year} {vehicle.make} {vehicle.model}',
            )
            
            # Add 3-5 messages per conversation
            num_messages = random.randint(3, 5)
            for j in range(num_messages):
                sender = buyer if j % 2 == 0 else dealer
                
                messages_pool = [
                    f"Hi, I'm interested in the {vehicle.year} {vehicle.make} {vehicle.model}.",
                    "What's the condition of the vehicle?",
                    "Can you provide more photos?",
                    "Is the price negotiable?",
                    "The vehicle is in excellent condition with all maintenance records.",
                    "I can send additional photos. What specific angles would you like?",
                    "We can discuss pricing. What's your budget?",
                    "When can we arrange for inspection?",
                    "Shipping to my location would cost approximately $2,500.",
                    "I'm ready to make an offer.",
                ]
                
                Message.objects.create(
                    conversation=conversation,
                    sender=sender,
                    content=messages_pool[j % len(messages_pool)],
                    created_at=timezone.now() - timedelta(days=random.randint(1, 10), hours=random.randint(0, 23)),
                )
            
            conversations.append(conversation)
        
        self.stdout.write(f'  ✓ Created {len(conversations)} conversations with messages')
        return conversations
    
    def create_notifications(self, buyers, dealers, brokers):
        from notifications.models import Notification
        
        notifications = []
        
        notification_data = [
            ('deal', 'Deal Update', 'Your deal status has been updated to shipped'),
            ('lead', 'New Inquiry', 'You received a new inquiry about a vehicle'),
            ('commission', 'Commission Earned', 'You earned a commission on a recent deal'),
            ('shipment', 'Shipment Update', 'Your shipment is on its way'),
            ('vehicle', 'Vehicle Available', 'A vehicle matching your interests is available'),
            ('document', 'Document Ready', 'Your export documents are ready for download'),
            ('system', 'System Update', 'Platform maintenance scheduled for tomorrow'),
        ]
        
        all_users = list(buyers) + list(dealers) + list(brokers)
        
        for i in range(30):
            user = all_users[i % len(all_users)]
            notif_type, title, message = notification_data[i % len(notification_data)]
            
            Notification.objects.create(
                user=user,
                type=notif_type,
                title=title,
                message=message,
                is_read=random.choice([True, False, False]),  # Most unread
                link=f'/dashboard' if random.random() > 0.5 else None,
            )
        
        self.stdout.write(f'  ✓ Created 30 notifications')
    
    def print_summary(self, admin, dealers, brokers, buyers, vehicles, deals):
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('🎉 SEEDING COMPLETE - LOGIN CREDENTIALS'))
        self.stdout.write('='*60)
        
        self.stdout.write('\n📧 ADMIN:')
        self.stdout.write(f'  Email: admin@nzila.com')
        self.stdout.write(f'  Password: admin123')
        
        self.stdout.write('\n👔 DEALERS (all password: dealer123):')
        for dealer in dealers[:3]:
            self.stdout.write(f'  • {dealer.email} - {dealer.company_name}')
        
        self.stdout.write('\n🤝 BROKERS (all password: broker123):')
        for broker in brokers[:3]:
            self.stdout.write(f'  • {broker.email} - {broker.company_name}')
        
        self.stdout.write('\n🛒 BUYERS (all password: buyer123):')
        for buyer in buyers[:3]:
            self.stdout.write(f'  • {buyer.email} - {buyer.address}')
        
        self.stdout.write('\n📊 DATA SUMMARY:')
        self.stdout.write(f'  • {len(dealers)} Dealers')
        self.stdout.write(f'  • {len(brokers)} Brokers')
        self.stdout.write(f'  • {len(buyers)} Buyers')
        self.stdout.write(f'  • {len(vehicles)} Vehicles (BMW, Mercedes, Toyota, Honda, etc.)')
        self.stdout.write(f'  • {len(deals)} Deals (various statuses)')
        
        self.stdout.write('\n🌐 ACCESS:')
        self.stdout.write('  Frontend: http://localhost:5173')
        self.stdout.write('  Backend API: http://localhost:8000/api/')
        self.stdout.write('  Admin Panel: http://localhost:8000/admin/')
        
        self.stdout.write('\n' + '='*60 + '\n')
