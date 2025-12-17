#!/usr/bin/env python
"""
ISO 28000 Certification Demo Data Seeder

Creates realistic demo shipments with complete certification data:
- Various risk levels (low, medium, high, critical)
- Lloyd's Register service levels (standard, premium, surveyor)
- Container types and seal information
- Security incidents and port verifications
- Complete audit trail

Usage:
    python seed_certification_demo.py

This will create 10 demo shipments with varied scenarios to showcase
all ISO 28000 certification features.
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
from random import choice, randint, uniform

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nzila_export.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from vehicles.models import Vehicle
from deals.models import Deal
from shipments.models import Shipment, ShipmentUpdate
from shipments.certification_models import (
    SecurityRiskAssessment,
    SecurityIncident,
    PortVerification,
    ISO28000AuditLog
)

User = get_user_model()


class CertificationDemoSeeder:
    """Seed database with realistic ISO 28000 certification demo data"""
    
    def __init__(self):
        self.user = None
        self.vehicles = []
        self.deals = []
        self.shipments = []
        
        # Demo routes with varying risk profiles
        self.routes = [
            {
                'origin': 'Vancouver, BC, Canada',
                'destination': 'Tokyo, Japan',
                'route_risk': 2,
                'customs_risk': 3,
                'description': 'Safe Pacific route'
            },
            {
                'origin': 'Los Angeles, CA, USA',
                'destination': 'Dubai, UAE',
                'route_risk': 4,
                'customs_risk': 5,
                'description': 'Medium risk Middle East route'
            },
            {
                'origin': 'Hamburg, Germany',
                'destination': 'Lagos, Nigeria',
                'route_risk': 7,
                'customs_risk': 8,
                'description': 'High risk West Africa route'
            },
            {
                'origin': 'Southampton, UK',
                'destination': 'Mombasa, Kenya',
                'route_risk': 6,
                'customs_risk': 7,
                'description': 'High risk East Africa route'
            },
            {
                'origin': 'Rotterdam, Netherlands',
                'destination': 'Sydney, Australia',
                'route_risk': 3,
                'customs_risk': 2,
                'description': 'Safe Australia route'
            },
        ]
        
        # Demo vehicles
        self.vehicle_specs = [
            {'year': 2023, 'make': 'Toyota', 'model': 'Land Cruiser', 'price': 75000},
            {'year': 2024, 'make': 'Mercedes-Benz', 'model': 'G-Class', 'price': 140000},
            {'year': 2023, 'make': 'BMW', 'model': 'X7', 'price': 95000},
            {'year': 2022, 'make': 'Lexus', 'model': 'LX 600', 'price': 110000},
            {'year': 2024, 'make': 'Range Rover', 'model': 'Sport', 'price': 125000},
            {'year': 2023, 'make': 'Porsche', 'model': 'Cayenne', 'price': 88000},
            {'year': 2023, 'make': 'Audi', 'model': 'Q8', 'price': 82000},
            {'year': 2024, 'make': 'Cadillac', 'model': 'Escalade', 'price': 98000},
            {'year': 2022, 'make': 'Lincoln', 'model': 'Navigator', 'price': 85000},
            {'year': 2023, 'make': 'Tesla', 'model': 'Model X', 'price': 105000},
        ]
        
    def setup_user(self):
        """Get or create demo user"""
        print("🔧 Setting up demo user...")
        
        self.user = User.objects.filter(email='demo@nzilaventures.com').first()
        if not self.user:
            self.user = User.objects.create_user(
                username='demouser',
                email='demo@nzilaventures.com',
                password='DemoPass123!',
                first_name='Demo',
                last_name='User'
            )
            print(f"  ✅ Created demo user: {self.user.email}")
        else:
            print(f"  ♻️  Using existing user: {self.user.email}")
        
        return self.user
    
    def generate_vin(self, index):
        """Generate realistic-looking VIN"""
        manufacturers = ['1GC', '2T1', '3FA', '4T1', '5YJ', 'WBA', 'JM1', 'KNA']
        mfg = choice(manufacturers)
        return f"{mfg}DEMO{index:03d}{randint(100000, 999999)}"
    
    def create_vehicles(self):
        """Create demo vehicles"""
        print("\n🚗 Creating demo vehicles...")
        
        for i, spec in enumerate(self.vehicle_specs, 1):
            vin = self.generate_vin(i)
            
            vehicle = Vehicle.objects.filter(vin=vin).first()
            if not vehicle:
                vehicle = Vehicle.objects.create(
                    vin=vin,
                    year=spec['year'],
                    make=spec['make'],
                    model=spec['model'],
                    price_cad=Decimal(str(spec['price'])),
                    mileage=randint(5000, 50000),
                    color=choice(['Black', 'White', 'Silver', 'Blue', 'Red']),
                    condition='used_good',
                    location='Vancouver, BC',
                    status='sold',  # Already sold for shipping
                    dealer=self.user
                )
                print(f"  ✅ Created: {vehicle.year} {vehicle.make} {vehicle.model} (VIN: {vin})")
            else:
                print(f"  ♻️  Exists: {vehicle.year} {vehicle.make} {vehicle.model}")
            
            self.vehicles.append(vehicle)
        
        return self.vehicles
    
    def create_deals(self):
        """Create demo deals"""
        print("\n💼 Creating demo deals...")
        
        for i, vehicle in enumerate(self.vehicles, 1):
            # Use vehicle.dealer as dealer for the deal
            deal = Deal.objects.filter(vehicle=vehicle).first()
            if not deal:
                deal = Deal.objects.create(
                    buyer=self.user,
                    dealer=vehicle.dealer,
                    vehicle=vehicle,
                    agreed_price_cad=vehicle.price_cad,
                    status='completed',
                    payment_status='paid'
                )
                print(f"  ✅ Created deal {deal.id}: {vehicle.year} {vehicle.make} {vehicle.model} - CAD ${vehicle.price_cad}")
            else:
                print(f"  ♻️  Exists: Deal {deal.id}")
            
            self.deals.append(deal)
        
        return self.deals
    
    def create_shipments(self):
        """Create demo shipments with full certification data"""
        print("\n🚢 Creating demo shipments with ISO 28000 certification...")
        
        container_types = ['20ft', '40ft', '40ft_HC']
        seal_types = ['bolt', 'cable', 'electronic']
        lr_service_levels = ['standard', 'premium', 'surveyor']
        
        for i, (deal, route) in enumerate(zip(self.deals, 
                                               [self.routes[i % len(self.routes)] for i in range(len(self.deals))]), 1):
            tracking_number = f'SHIP-DEMO-{i:03d}'
            
            shipment = Shipment.objects.filter(tracking_number=tracking_number).first()
            if shipment:
                print(f"  ♻️  Shipment exists: {tracking_number}")
                self.shipments.append(shipment)
                continue
            
            # Calculate value-based risk
            vehicle_value = float(deal.vehicle.price_cad)
            if vehicle_value < 60000:
                value_risk = randint(3, 5)
            elif vehicle_value < 100000:
                value_risk = randint(6, 8)
            else:
                value_risk = randint(9, 10)
            
            # Calculate destination risk based on route
            destination_risk = route['route_risk']
            
            # Total risk score
            route_risk = route['route_risk']
            customs_risk = route['customs_risk']
            port_security = randint(3, 7)
            total_risk = (route_risk + value_risk + destination_risk + customs_risk + port_security) * 2
            
            # Determine risk level
            if total_risk <= 30:
                risk_level = 'low'
                lr_service = 'standard'
            elif total_risk <= 60:
                risk_level = 'medium'
                lr_service = choice(['standard', 'premium'])
            elif total_risk <= 85:
                risk_level = 'high'
                lr_service = choice(['premium', 'surveyor'])
            else:
                risk_level = 'critical'
                lr_service = 'surveyor'
            
            # Create shipment
            shipment = Shipment.objects.create(
                deal=deal,
                tracking_number=tracking_number,
                origin_port=route['origin'],
                destination_port=route['destination'],
                status=choice(['pending', 'in_transit', 'arrived']),
                
                # Container & Seal
                container_number=f'{choice(["ABCD", "XYZW", "PQRS"])}{randint(1000000, 9999999)}',
                container_type=choice(container_types),
                seal_number=f'SEAL-{randint(10000000, 99999999)}',
                seal_type=choice(seal_types),
                seal_applied_at=timezone.now() - timedelta(days=randint(1, 30)),
                
                # Lloyd's Register
                lloyd_register_tracking_id=f'LR-2024-{randint(1000000, 9999999)}',
                lloyd_register_service_level=lr_service,
                lloyd_register_status=choice(['origin_verified', 'in_transit', 'destination_arrival']),
                
                # Security
                security_risk_level=risk_level,
                security_assessment_completed=True,
                security_measures_implemented=True,
                ctpat_compliant=(total_risk <= 60),  # Only low/medium risk
                
                # Insurance
                insurance_policy_number=f'INS-{randint(100000, 999999)}',
                insurance_company=choice(['Allianz Marine', 'Lloyd\'s of London', 'AIG Marine']),
                insurance_coverage_amount=Decimal(str(vehicle_value * 1.25)),
                
                # ISO Compliance
                iso_18602_compliant=True,
                
                # Schedule
                estimated_departure=timezone.now() - timedelta(days=randint(5, 20)),
                estimated_arrival=timezone.now() + timedelta(days=randint(10, 40)),
            )
            
            print(f"  ✅ Created shipment: {tracking_number}")
            print(f"     Route: {route['origin']} → {route['destination']}")
            print(f"     Risk Level: {risk_level.upper()} ({total_risk}/100)")
            print(f"     LR Service: {lr_service}")
            print(f"     Container: {shipment.container_number} ({shipment.container_type})")
            
            # Create SecurityRiskAssessment
            assessment = SecurityRiskAssessment.objects.create(
                shipment=shipment,
                route_risk_score=route_risk,
                value_risk_score=value_risk,
                destination_risk_score=destination_risk,
                customs_risk_score=customs_risk,
                port_security_score=port_security,
                assessed_by=self.user,
                mitigation_measures=f"Risk assessment for {route['description']}. Vehicle value: CAD ${vehicle_value:,.0f}.",
                overall_risk_level=risk_level,
                risk_score=total_risk,
                recommended_insurance_amount=Decimal(str(vehicle_value * 1.25))
            )
            # Trigger calculate_risk_score to recalculate and validate
            assessment.calculate_risk_score()
            assessment.save()
            
            print(f"     ✅ Risk assessment: {assessment.risk_score}/100 ({assessment.overall_risk_level})")
            
            # Create audit log for risk assessment
            ISO28000AuditLog.objects.create(
                shipment=shipment,
                action_type='risk_assessment',
                action_timestamp=timezone.now() - timedelta(days=randint(1, 15)),
                performed_by=self.user,
                action_description=f"Security risk assessment completed - Risk Score: {assessment.risk_score}/100 ({assessment.overall_risk_level})",
                related_object_type='SecurityRiskAssessment',
                related_object_id=assessment.id,
                ip_address='127.0.0.1'
            )
            
            # Create audit log for LR registration
            ISO28000AuditLog.objects.create(
                shipment=shipment,
                action_type='lr_registered',
                action_timestamp=timezone.now() - timedelta(days=randint(1, 10)),
                performed_by=self.user,
                action_description=f"Registered with Lloyd's Register CTS - Service Level: {lr_service}, Tracking ID: {shipment.lloyd_register_tracking_id}",
                ip_address='127.0.0.1'
            )
            
            # Add security incidents for high/critical risk shipments
            if risk_level in ['high', 'critical']:
                incident_types = [
                    ('delay', 'minor', 'Customs inspection delayed departure by 6 hours'),
                    ('customs', 'moderate', 'Additional documentation requested by customs'),
                    ('seal_breach', 'severe', 'Seal integrity compromised during transit'),
                ]
                
                incident_type, severity, description = choice(incident_types)
                
                incident = SecurityIncident.objects.create(
                    shipment=shipment,
                    incident_type=incident_type,
                    severity=severity,
                    incident_date=timezone.now() - timedelta(days=randint(1, 5)),
                    description=description,
                    reported_by=self.user,
                    location=route['origin'] if randint(0, 1) else 'In Transit',
                    police_report_filed=(severity in ['severe', 'critical']),
                    police_report_number=f'PD-{randint(100000, 999999)}' if severity in ['severe', 'critical'] else '',
                    insurance_claim_filed=(severity == 'severe'),
                    insurance_claim_number=f'INS-{randint(100000, 999999)}' if severity == 'severe' else '',
                    estimated_cost=Decimal(str(randint(500, 5000))) if severity != 'minor' else None,
                    resolved=(severity == 'minor'),
                    resolution_notes='Resolved after customs clearance' if severity == 'minor' else ''
                )
                
                print(f"     ⚠️  Incident reported: {incident_type} ({severity})")
                
                # Audit log for incident
                ISO28000AuditLog.objects.create(
                    shipment=shipment,
                    action_type='incident_report',
                    action_timestamp=incident.reported_date,
                    performed_by=self.user,
                    action_description=f"Security incident reported: {incident_type} ({severity}) - {description[:50]}...",
                    related_object_type='SecurityIncident',
                    related_object_id=incident.id,
                    ip_address='127.0.0.1'
                )
            
            # Add port verifications
            if shipment.status in ['in_transit', 'arrived']:
                # Origin verification
                origin_verification = PortVerification.objects.create(
                    shipment=shipment,
                    verification_type='origin_departure',
                    verification_date=shipment.estimated_departure - timedelta(hours=2),
                    port_name=route['origin'].split(',')[0],
                    port_country=route['origin'].split(',')[-1].strip(),
                    verified_by_name='Port Inspector',
                    verifier_organization='Port Authority',
                    verifier_credentials='Maritime Inspector #12345',
                    seal_number_verified=shipment.seal_number,
                    seal_intact=True,
                    seal_condition_notes='ISO 17712 high-security bolt seal applied and verified',
                    vehicle_condition_status='excellent',
                    odometer_reading=randint(5000, 50000),
                    vehicle_condition_notes=f'{deal.vehicle.year} {deal.vehicle.make} {deal.vehicle.model} in excellent condition',
                    customs_cleared=True,
                    customs_clearance_date=shipment.estimated_departure - timedelta(hours=12),
                    documents_complete=True,
                    issues_identified=''
                )
                
                print(f"     ✅ Port verification: Origin departure verified")
                
                # Audit log for port verification
                ISO28000AuditLog.objects.create(
                    shipment=shipment,
                    action_type='port_verification',
                    action_timestamp=origin_verification.verification_date,
                    performed_by=self.user,
                    action_description=f"Port verification completed: origin_departure at {route['origin']}",
                    related_object_type='PortVerification',
                    related_object_id=origin_verification.id,
                    ip_address='127.0.0.1'
                )
            
            # Add shipment updates
            for days_ago in [15, 10, 5, 2]:
                ShipmentUpdate.objects.create(
                    shipment=shipment,
                    location=choice([route['origin'], 'In Transit', route['destination']]),
                    status=choice(['Departed from port', 'In transit', 'Customs clearance', 'Arrived at destination']),
                    description=f"Update {days_ago} days ago",
                    latitude=Decimal(str(uniform(-90, 90))),
                    longitude=Decimal(str(uniform(-180, 180))),
                    iso_message_type='IFTSTA',
                    verified_by='Port Authority',
                    verification_method='gps'
                )
            
            self.shipments.append(shipment)
            print()
        
        return self.shipments
    
    def run(self):
        """Execute complete seeding process"""
        print("\n" + "=" * 70)
        print("ISO 28000 CERTIFICATION DEMO DATA SEEDER")
        print("=" * 70)
        print("This will create 10 demo shipments with complete certification data")
        print("=" * 70 + "\n")
        
        self.setup_user()
        self.create_vehicles()
        self.create_deals()
        self.create_shipments()
        
        # Summary
        print("\n" + "=" * 70)
        print("DEMO DATA CREATION SUMMARY")
        print("=" * 70)
        print(f"✅ Vehicles Created: {len(self.vehicles)}")
        print(f"✅ Deals Created: {len(self.deals)}")
        print(f"✅ Shipments Created: {len(self.shipments)}")
        
        # Risk distribution
        risk_counts = {
            'low': sum(1 for s in self.shipments if s.security_risk_level == 'low'),
            'medium': sum(1 for s in self.shipments if s.security_risk_level == 'medium'),
            'high': sum(1 for s in self.shipments if s.security_risk_level == 'high'),
            'critical': sum(1 for s in self.shipments if s.security_risk_level == 'critical'),
        }
        
        print(f"\n📊 Risk Level Distribution:")
        print(f"   Low Risk: {risk_counts['low']} shipments")
        print(f"   Medium Risk: {risk_counts['medium']} shipments")
        print(f"   High Risk: {risk_counts['high']} shipments")
        print(f"   Critical Risk: {risk_counts['critical']} shipments")
        
        # LR service distribution
        lr_counts = {
            'standard': sum(1 for s in self.shipments if s.lloyd_register_service_level == 'standard'),
            'premium': sum(1 for s in self.shipments if s.lloyd_register_service_level == 'premium'),
            'surveyor': sum(1 for s in self.shipments if s.lloyd_register_service_level == 'surveyor'),
        }
        
        print(f"\n📋 Lloyd's Register Service Levels:")
        print(f"   Standard: {lr_counts['standard']} shipments")
        print(f"   Premium: {lr_counts['premium']} shipments")
        print(f"   Surveyor: {lr_counts['surveyor']} shipments")
        
        # Database records
        print(f"\n🗄️  Database Records:")
        print(f"   SecurityRiskAssessments: {SecurityRiskAssessment.objects.count()}")
        print(f"   SecurityIncidents: {SecurityIncident.objects.count()}")
        print(f"   PortVerifications: {PortVerification.objects.count()}")
        print(f"   ISO28000AuditLogs: {ISO28000AuditLog.objects.count()}")
        print(f"   ShipmentUpdates: {ShipmentUpdate.objects.count()}")
        
        print("\n" + "=" * 70)
        print("🎉 DEMO DATA SEEDING COMPLETE!")
        print("=" * 70)
        print("\nNext Steps:")
        print("1. Run API tests: python test_certification_api.py")
        print("2. Login to admin: http://127.0.0.1:8000/admin/")
        print("   Username: demo@nzilaventures.com")
        print("   Password: DemoPass123!")
        print("3. View shipments at: http://127.0.0.1:8000/admin/shipments/shipment/")
        print("=" * 70 + "\n")


if __name__ == '__main__':
    seeder = CertificationDemoSeeder()
    seeder.run()
