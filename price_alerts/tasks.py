from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from decimal import Decimal
from .models import PriceHistory
from vehicles.models import Vehicle
from favorites.models import Favorite


@shared_task
def check_vehicle_prices():
    """
    Periodic task to check all vehicles for price changes.
    Creates PriceHistory records when prices change.
    Runs every hour.
    """
    vehicles = Vehicle.objects.all()
    changes_detected = 0
    
    for vehicle in vehicles:
        # Get the most recent price history for this vehicle
        latest_history = PriceHistory.objects.filter(
            vehicle=vehicle
        ).order_by('-changed_at').first()
        
        # Check if price has changed
        if latest_history:
            last_known_price = latest_history.new_price
        else:
            # No history yet, use current price as baseline
            last_known_price = vehicle.price
        
        current_price = vehicle.price
        
        # If price changed, create history record
        if current_price != last_known_price:
            price_diff = current_price - last_known_price
            percentage_change = (price_diff / last_known_price) * 100 if last_known_price > 0 else 0
            
            price_history = PriceHistory.objects.create(
                vehicle=vehicle,
                old_price=last_known_price,
                new_price=current_price,
                price_difference=price_diff,
                percentage_change=percentage_change
            )
            
            changes_detected += 1
            
            # If it's a price drop, trigger notifications
            if price_diff < 0:
                notify_price_drop.delay(price_history.id)
    
    return f"Checked {vehicles.count()} vehicles, found {changes_detected} price changes"


@shared_task
def notify_price_drop(price_history_id):
    """
    Send email notifications to users watching a vehicle that dropped in price.
    """
    try:
        price_history = PriceHistory.objects.get(id=price_history_id)
    except PriceHistory.DoesNotExist:
        return f"PriceHistory {price_history_id} not found"
    
    # Get all users who have favorited this vehicle
    favorites = Favorite.objects.filter(
        vehicle=price_history.vehicle
    ).select_related('user')
    
    if not favorites.exists():
        return f"No users watching vehicle {price_history.vehicle.vin}"
    
    notifications_sent = 0
    
    for favorite in favorites:
        user = favorite.user
        
        # Check if user was already notified about this price change
        if price_history.notified_users.filter(id=user.id).exists():
            continue
        
        # Send email notification
        try:
            send_price_drop_email(user, price_history)
            price_history.notified_users.add(user)
            notifications_sent += 1
        except Exception as e:
            print(f"Failed to send email to {user.email}: {str(e)}")
    
    return f"Sent {notifications_sent} price drop notifications for vehicle {price_history.vehicle.vin}"


def send_price_drop_email(user, price_history):
    """
    Send price drop notification email to a user.
    """
    vehicle = price_history.vehicle
    amount_saved = abs(price_history.price_difference)
    percentage = abs(price_history.percentage_change)
    
    # Render email from template
    html_message = render_to_string('email_templates/price_drop_notification.html', {
        'user_name': user.first_name or user.username,
        'vehicle': vehicle,
        'old_price': price_history.old_price,
        'new_price': price_history.new_price,
        'amount_saved': amount_saved,
        'percentage': percentage,
        'vehicle_url': f"{settings.FRONTEND_URL}/vehicles/{vehicle.id}",
        'settings_url': f"{settings.FRONTEND_URL}/settings",
    })
    
    send_mail(
        subject=f"Price Drop Alert: {vehicle.year} {vehicle.make} {vehicle.model}",
        message=f"The price for {vehicle.year} {vehicle.make} {vehicle.model} has dropped by ${amount_saved}!",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


@shared_task
def cleanup_old_price_history():
    """
    Remove price history records older than 1 year.
    Runs daily.
    """
    from datetime import timedelta
    one_year_ago = timezone.now() - timedelta(days=365)
    
    deleted_count, _ = PriceHistory.objects.filter(
        changed_at__lt=one_year_ago
    ).delete()
    
    return f"Deleted {deleted_count} price history records older than 1 year"
