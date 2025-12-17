from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from .models import SavedSearch
from vehicles.models import Vehicle
from email_templates.services import EmailTemplateService
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_saved_searches_for_new_vehicles():
    """
    Celery task to check all active saved searches and send email notifications
    for new matching vehicles. Should be run periodically (e.g., every hour).
    """
    active_searches = SavedSearch.objects.filter(
        is_active=True,
        email_notifications=True,
        notification_frequency='immediate'
    )
    
    notifications_sent = 0
    
    for saved_search in active_searches:
        try:
            # Get vehicles added since last notification
            last_check = saved_search.last_notified_at or saved_search.created_at
            new_vehicles = get_matching_vehicles(saved_search).filter(
                created_at__gt=last_check
            )
            
            if new_vehicles.exists():
                # Send email notification
                send_new_vehicles_notification(saved_search, new_vehicles)
                
                # Update last notified time and match count
                saved_search.last_notified_at = timezone.now()
                saved_search.match_count = get_matching_vehicles(saved_search).count()
                saved_search.save(update_fields=['last_notified_at', 'match_count'])
                
                notifications_sent += 1
                logger.info(
                    f"Sent notification for saved search '{saved_search.name}' "
                    f"to {saved_search.user.email} ({new_vehicles.count()} new vehicles)"
                )
        
        except Exception as e:
            logger.error(
                f"Error processing saved search {saved_search.id}: {str(e)}"
            )
    
    logger.info(f"Processed saved searches: {notifications_sent} notifications sent")
    return notifications_sent


@shared_task
def send_daily_digest():
    """
    Send daily digest emails for users with daily notification preference.
    Should be run once per day (e.g., at 9 AM).
    """
    daily_searches = SavedSearch.objects.filter(
        is_active=True,
        email_notifications=True,
        notification_frequency='daily'
    )
    
    # Group by user to send one email per user
    users_with_matches = {}
    
    for saved_search in daily_searches:
        last_check = saved_search.last_notified_at or (timezone.now() - timezone.timedelta(days=1))
        new_vehicles = get_matching_vehicles(saved_search).filter(
            created_at__gt=last_check
        )
        
        if new_vehicles.exists():
            user_id = saved_search.user.id
            if user_id not in users_with_matches:
                users_with_matches[user_id] = []
            
            users_with_matches[user_id].append({
                'search': saved_search,
                'vehicles': new_vehicles
            })
    
    # Send one digest email per user
    for user_id, matches in users_with_matches.items():
        try:
            send_daily_digest_email(matches)
            
            # Update last notified time for all searches
            for match in matches:
                search = match['search']
                search.last_notified_at = timezone.now()
                search.match_count = get_matching_vehicles(search).count()
                search.save(update_fields=['last_notified_at', 'match_count'])
            
            logger.info(f"Sent daily digest to user {user_id}")
        
        except Exception as e:
            logger.error(f"Error sending daily digest to user {user_id}: {str(e)}")
    
    return len(users_with_matches)


@shared_task
def send_weekly_digest():
    """
    Send weekly digest emails for users with weekly notification preference.
    Should be run once per week (e.g., Monday at 9 AM).
    """
    weekly_searches = SavedSearch.objects.filter(
        is_active=True,
        email_notifications=True,
        notification_frequency='weekly'
    )
    
    # Group by user
    users_with_matches = {}
    
    for saved_search in weekly_searches:
        last_check = saved_search.last_notified_at or (timezone.now() - timezone.timedelta(days=7))
        new_vehicles = get_matching_vehicles(saved_search).filter(
            created_at__gt=last_check
        )
        
        if new_vehicles.exists():
            user_id = saved_search.user.id
            if user_id not in users_with_matches:
                users_with_matches[user_id] = []
            
            users_with_matches[user_id].append({
                'search': saved_search,
                'vehicles': new_vehicles
            })
    
    # Send one digest email per user
    for user_id, matches in users_with_matches.items():
        try:
            send_weekly_digest_email(matches)
            
            # Update last notified time for all searches
            for match in matches:
                search = match['search']
                search.last_notified_at = timezone.now()
                search.match_count = get_matching_vehicles(search).count()
                search.save(update_fields=['last_notified_at', 'match_count'])
            
            logger.info(f"Sent weekly digest to user {user_id}")
        
        except Exception as e:
            logger.error(f"Error sending weekly digest to user {user_id}: {str(e)}")
    
    return len(users_with_matches)


def get_matching_vehicles(saved_search):
    """Build queryset of vehicles matching the saved search criteria"""
    queryset = Vehicle.objects.filter(status='available')
    
    if saved_search.make:
        queryset = queryset.filter(make__iexact=saved_search.make)
    
    if saved_search.model:
        queryset = queryset.filter(model__icontains=saved_search.model)
    
    if saved_search.year_min:
        queryset = queryset.filter(year__gte=saved_search.year_min)
    
    if saved_search.year_max:
        queryset = queryset.filter(year__lte=saved_search.year_max)
    
    if saved_search.price_min:
        queryset = queryset.filter(price__gte=saved_search.price_min)
    
    if saved_search.price_max:
        queryset = queryset.filter(price__lte=saved_search.price_max)
    
    if saved_search.condition:
        queryset = queryset.filter(condition=saved_search.condition)
    
    if saved_search.mileage_max:
        queryset = queryset.filter(mileage__lte=saved_search.mileage_max)
    
    return queryset.order_by('-created_at')


def send_new_vehicles_notification(saved_search, vehicles):
    """Send email notification about new matching vehicles"""
    user = saved_search.user
    vehicle_list = list(vehicles[:10])  # Limit to 10 vehicles per email
    
    context = {
        'user_name': user.get_full_name() or user.email,
        'search_name': saved_search.name,
        'search_criteria': saved_search.get_search_criteria_display(),
        'vehicle_count': vehicles.count(),
        'vehicles': [
            {
                'year': v.year,
                'make': v.make,
                'model': v.model,
                'price': v.price,
                'vin': v.vin,
                'condition': v.get_condition_display(),
                'mileage': v.mileage,
                'image': v.image,
            }
            for v in vehicle_list
        ],
        'more_count': max(0, vehicles.count() - 10),
    }
    
    EmailTemplateService.send_email(
        to_email=user.email,
        subject=f"New vehicles matching '{saved_search.name}'",
        template_name='email_templates/saved_search_notification.html',
        context=context
    )


def send_daily_digest_email(matches):
    """Send daily digest email with all matching searches"""
    user = matches[0]['search'].user
    
    total_vehicles = sum(len(m['vehicles']) for m in matches)
    
    searches_data = []
    for match in matches:
        search = match['search']
        vehicles = list(match['vehicles'][:5])  # Top 5 per search
        
        searches_data.append({
            'name': search.name,
            'criteria': search.get_search_criteria_display(),
            'count': match['vehicles'].count(),
            'vehicles': [
                {
                    'year': v.year,
                    'make': v.make,
                    'model': v.model,
                    'price': v.price,
                    'vin': v.vin,
                }
                for v in vehicles
            ],
        })
    
    context = {
        'user_name': user.get_full_name() or user.email,
        'total_vehicles': total_vehicles,
        'searches': searches_data,
    }
    
    EmailTemplateService.send_email(
        to_email=user.email,
        subject=f"Daily Digest: {total_vehicles} new vehicles match your saved searches",
        template_name='email_templates/saved_search_digest.html',
        context=context
    )


def send_weekly_digest_email(matches):
    """Send weekly digest email with all matching searches"""
    # Same as daily digest but with different subject
    user = matches[0]['search'].user
    
    total_vehicles = sum(len(m['vehicles']) for m in matches)
    
    searches_data = []
    for match in matches:
        search = match['search']
        vehicles = list(match['vehicles'][:5])
        
        searches_data.append({
            'name': search.name,
            'criteria': search.get_search_criteria_display(),
            'count': match['vehicles'].count(),
            'vehicles': [
                {
                    'year': v.year,
                    'make': v.make,
                    'model': v.model,
                    'price': v.price,
                    'vin': v.vin,
                }
                for v in vehicles
            ],
        })
    
    context = {
        'user_name': user.get_full_name() or user.email,
        'total_vehicles': total_vehicles,
        'searches': searches_data,
    }
    
    EmailTemplateService.send_email(
        to_email=user.email,
        subject=f"Weekly Digest: {total_vehicles} new vehicles match your saved searches",
        template_name='email_templates/saved_search_digest.html',
        context=context
    )
