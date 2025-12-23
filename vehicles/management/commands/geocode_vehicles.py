"""
Django management command to geocode vehicle locations.

This command processes all vehicles without coordinates and geocodes their
location addresses into latitude/longitude coordinates.

Phase 2: Proximity Search & Travel Radius
Author: Django Development Team
Date: December 2025

Usage:
    python manage.py geocode_vehicles
    python manage.py geocode_vehicles --force  # Re-geocode all vehicles
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from vehicles.models import Vehicle
from utils.geocoding_service import geocoding_service
import time


class Command(BaseCommand):
    help = 'Geocode vehicle locations to latitude/longitude coordinates'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-geocoding of all vehicles, even those with existing coordinates',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of vehicles to geocode (for testing)',
        )
    
    def handle(self, *args, **options):
        force = options['force']
        limit = options['limit']
        
        # Build queryset
        if force:
            vehicles = Vehicle.objects.all()
            self.stdout.write('Geocoding ALL vehicles (force mode)...')
        else:
            vehicles = Vehicle.objects.filter(
                latitude__isnull=True,
                longitude__isnull=True
            )
            self.stdout.write('Geocoding vehicles without coordinates...')
        
        # Apply limit if specified
        if limit:
            vehicles = vehicles[:limit]
            self.stdout.write(f'Processing first {limit} vehicles...')
        
        total = vehicles.count()
        self.stdout.write(f'Found {total} vehicles to geocode')
        
        if total == 0:
            self.stdout.write(self.style.SUCCESS('No vehicles need geocoding!'))
            return
        
        # Process vehicles
        success_count = 0
        fail_count = 0
        
        for i, vehicle in enumerate(vehicles, 1):
            # Parse location string
            # Expected format: "City, Province" or "City, Province, Country"
            try:
                location_parts = [p.strip() for p in vehicle.location.split(',')]
                
                if len(location_parts) < 2:
                    self.stdout.write(
                        self.style.WARNING(
                            f'[{i}/{total}] Skipping {vehicle.id}: '
                            f'Invalid location format "{vehicle.location}"'
                        )
                    )
                    fail_count += 1
                    continue
                
                # Try to geocode as city
                city = location_parts[0]
                province = location_parts[1]
                
                self.stdout.write(f'[{i}/{total}] Geocoding {vehicle.id}: {city}, {province}...')
                
                coords = geocoding_service.geocode_city(city, province)
                
                if coords:
                    latitude, longitude = coords
                    vehicle.latitude = latitude
                    vehicle.longitude = longitude
                    vehicle.save(update_fields=['latitude', 'longitude'])
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'[{i}/{total}] ✓ {vehicle.id}: {city}, {province} → '
                            f'({latitude}, {longitude})'
                        )
                    )
                    success_count += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'[{i}/{total}] ✗ {vehicle.id}: Could not geocode "{city}, {province}"'
                        )
                    )
                    fail_count += 1
                
                # Rate limiting (Nominatim requires 1 req/sec)
                if i < total:
                    time.sleep(1)
            
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'[{i}/{total}] ✗ {vehicle.id}: Error - {str(e)}'
                    )
                )
                fail_count += 1
        
        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Geocoding complete!'))
        self.stdout.write(f'  Success: {success_count}')
        self.stdout.write(f'  Failed:  {fail_count}')
        self.stdout.write(f'  Total:   {total}')
