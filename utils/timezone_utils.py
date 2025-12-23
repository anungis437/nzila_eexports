"""
Canadian Timezone Utilities
Handles timezone detection and conversion for Canadian provinces
"""
import pytz
from django.utils import timezone as django_timezone
from typing import Optional
from datetime import datetime, time

# Canadian Province to Timezone Mapping
CANADIAN_TIMEZONES = {
    'ON': 'America/Toronto',       # Ontario - Eastern (ET)
    'QC': 'America/Toronto',       # Quebec - Eastern (ET)
    'NS': 'America/Halifax',       # Nova Scotia - Atlantic (AT)
    'NB': 'America/Halifax',       # New Brunswick - Atlantic (AT)
    'PE': 'America/Halifax',       # Prince Edward Island - Atlantic (AT)
    'NL': 'America/St_Johns',      # Newfoundland - Newfoundland (NT) UTC-3:30
    'MB': 'America/Winnipeg',      # Manitoba - Central (CT)
    'SK': 'America/Regina',        # Saskatchewan - Central (no DST)
    'AB': 'America/Edmonton',      # Alberta - Mountain (MT)
    'BC': 'America/Vancouver',     # British Columbia - Pacific (PT)
    'YT': 'America/Whitehorse',    # Yukon - Mountain (MT) - uses Pacific since 2020
    'NT': 'America/Yellowknife',   # Northwest Territories - Mountain (MT)
    'NU': 'America/Iqaluit',       # Nunavut - Eastern (ET) - varies by region
}

# Timezone display names
TIMEZONE_DISPLAY_NAMES = {
    'America/Toronto': 'Eastern Time (ET)',
    'America/Halifax': 'Atlantic Time (AT)',
    'America/St_Johns': 'Newfoundland Time (NT)',
    'America/Winnipeg': 'Central Time (CT)',
    'America/Regina': 'Central Time (CT) - No DST',
    'America/Edmonton': 'Mountain Time (MT)',
    'America/Vancouver': 'Pacific Time (PT)',
    'America/Whitehorse': 'Yukon Time (YT)',
    'America/Yellowknife': 'Mountain Time (MT)',
    'America/Iqaluit': 'Eastern Time (ET)',
}


def get_timezone_for_province(province_code: str) -> Optional[pytz.timezone]:
    """
    Get timezone object for a Canadian province
    
    Args:
        province_code: Two-letter province code (ON, QC, BC, etc.)
    
    Returns:
        pytz.timezone object or None if province not found
    """
    tz_name = CANADIAN_TIMEZONES.get(province_code)
    if tz_name:
        return pytz.timezone(tz_name)
    return None


def get_timezone_display_name(province_code: str) -> str:
    """
    Get human-readable timezone name for a province
    
    Args:
        province_code: Two-letter province code
    
    Returns:
        Timezone display name (e.g., "Eastern Time (ET)")
    """
    tz_name = CANADIAN_TIMEZONES.get(province_code)
    if tz_name:
        return TIMEZONE_DISPLAY_NAMES.get(tz_name, tz_name)
    return 'UTC'


def convert_to_local_time(
    dt: datetime,
    province_code: str,
    from_tz: Optional[str] = None
) -> datetime:
    """
    Convert datetime to local time for a Canadian province
    
    Args:
        dt: Datetime object to convert
        province_code: Two-letter province code for target timezone
        from_tz: Source timezone name (default: UTC)
    
    Returns:
        Datetime object in local timezone
    """
    if not from_tz:
        from_tz = pytz.UTC
    elif isinstance(from_tz, str):
        from_tz = pytz.timezone(from_tz)
    
    local_tz = get_timezone_for_province(province_code)
    if not local_tz:
        return dt
    
    # Make aware if naive
    if django_timezone.is_naive(dt):
        dt = from_tz.localize(dt)
    
    # Convert to local timezone
    return dt.astimezone(local_tz)


def format_time_for_province(
    dt: datetime,
    province_code: str,
    include_timezone: bool = True
) -> str:
    """
    Format datetime for display in a Canadian province's timezone
    
    Args:
        dt: Datetime object to format
        province_code: Two-letter province code
        include_timezone: Whether to include timezone abbreviation
    
    Returns:
        Formatted time string (e.g., "2:30 PM ET" or "2:30 PM")
    """
    local_dt = convert_to_local_time(dt, province_code)
    
    time_str = local_dt.strftime("%I:%M %p")  # 02:30 PM
    
    if include_timezone:
        # Get timezone abbreviation (EST, PST, etc.)
        tz_abbr = local_dt.strftime("%Z")  # EST, EDT, PST, PDT, etc.
        return f"{time_str} {tz_abbr}"
    
    return time_str


def format_business_hours_for_province(
    business_hours: str,
    dealer_province: str,
    buyer_province: str
) -> str:
    """
    Convert dealer's business hours to buyer's timezone
    
    Args:
        business_hours: Original business hours string (e.g., "Mon-Fri 9am-6pm")
        dealer_province: Dealer's province code
        buyer_province: Buyer's province code
    
    Returns:
        Business hours in buyer's timezone (if different)
    
    Example:
        Input: "9am-6pm", dealer_province="BC", buyer_province="ON"
        Output: "12pm-9pm ET (9am-6pm PT at dealer)"
    """
    # If same timezone, return as-is
    dealer_tz = get_timezone_for_province(dealer_province)
    buyer_tz = get_timezone_for_province(buyer_province)
    
    if not dealer_tz or not buyer_tz or dealer_tz == buyer_tz:
        return business_hours
    
    # Simple conversion note for now
    # (Full parsing of business hours would require more complex logic)
    dealer_tz_name = get_timezone_display_name(dealer_province)
    buyer_tz_name = get_timezone_display_name(buyer_province)
    
    return f"{business_hours} ({dealer_tz_name}) - Times shown in {buyer_tz_name}"


def get_current_time_for_province(province_code: str) -> datetime:
    """
    Get current local time for a Canadian province
    
    Args:
        province_code: Two-letter province code
    
    Returns:
        Current datetime in province's local timezone
    """
    local_tz = get_timezone_for_province(province_code)
    if not local_tz:
        return django_timezone.now()
    
    return django_timezone.now().astimezone(local_tz)


def is_business_hours(
    province_code: str,
    start_time: time = time(9, 0),
    end_time: time = time(17, 0),
    check_time: Optional[datetime] = None
) -> bool:
    """
    Check if it's currently business hours in a province
    
    Args:
        province_code: Two-letter province code
        start_time: Business start time (default 9am)
        end_time: Business end time (default 5pm)
        check_time: Time to check (default: now)
    
    Returns:
        True if within business hours, False otherwise
    """
    if not check_time:
        check_time = get_current_time_for_province(province_code)
    
    current_time = check_time.time()
    
    # Check if weekday (Monday=0, Sunday=6)
    if check_time.weekday() >= 5:  # Saturday or Sunday
        return False
    
    return start_time <= current_time <= end_time


def get_timezone_offset_hours(province_code: str) -> float:
    """
    Get UTC offset in hours for a province
    
    Args:
        province_code: Two-letter province code
    
    Returns:
        UTC offset in hours (e.g., -5.0 for ET, -3.5 for NT)
    """
    local_tz = get_timezone_for_province(province_code)
    if not local_tz:
        return 0.0
    
    now = django_timezone.now()
    offset = local_tz.utcoffset(now)
    
    if offset:
        return offset.total_seconds() / 3600
    
    return 0.0
