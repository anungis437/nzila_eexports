"""
SMS Notification Service using Twilio
Handles sending SMS notifications to Canadian buyers
"""
import logging
from typing import Optional
from decouple import config
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import phonenumbers
from phonenumbers import NumberParseException

logger = logging.getLogger(__name__)


class SMSService:
    """Service for sending SMS notifications via Twilio"""
    
    def __init__(self):
        self.account_sid = config('TWILIO_ACCOUNT_SID', default='')
        self.auth_token = config('TWILIO_AUTH_TOKEN', default='')
        self.phone_number = config('TWILIO_PHONE_NUMBER', default='')
        self.test_mode = config('TWILIO_TEST_MODE', default=True, cast=bool)
        
        if self.account_sid and self.auth_token and not self.test_mode:
            self.client = Client(self.account_sid, self.auth_token)
        else:
            self.client = None
            if not self.test_mode:
                logger.warning("Twilio credentials not configured. SMS will not be sent.")
    
    def normalize_phone_number(self, phone: str, country_code: str = 'CA') -> Optional[str]:
        """
        Normalize phone number to E.164 format (+1234567890)
        
        Args:
            phone: Phone number string (any format)
            country_code: ISO country code (default: CA for Canada)
            
        Returns:
            Normalized phone number in E.164 format or None if invalid
        """
        try:
            parsed = phonenumbers.parse(phone, country_code)
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except NumberParseException as e:
            logger.error(f"Failed to parse phone number {phone}: {e}")
        return None
    
    def send_sms(
        self,
        to_phone: str,
        message: str,
        country_code: str = 'CA'
    ) -> bool:
        """
        Send SMS message
        
        Args:
            to_phone: Recipient phone number
            message: SMS message content (max 160 chars recommended)
            country_code: ISO country code for phone normalization
            
        Returns:
            True if SMS sent successfully, False otherwise
        """
        # Normalize phone number
        normalized_phone = self.normalize_phone_number(to_phone, country_code)
        if not normalized_phone:
            logger.error(f"Invalid phone number: {to_phone}")
            return False
        
        # Test mode: log instead of sending
        if self.test_mode or not self.client:
            logger.info(f"[SMS TEST MODE] To: {normalized_phone}, Message: {message}")
            return True
        
        # Send SMS via Twilio
        try:
            message_obj = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=normalized_phone
            )
            logger.info(f"SMS sent successfully. SID: {message_obj.sid}")
            return True
        except TwilioRestException as e:
            logger.error(f"Failed to send SMS to {normalized_phone}: {e}")
            return False
    
    def send_offer_accepted_notification(self, buyer_phone: str, vehicle: str, offer_amount: str) -> bool:
        """Send notification when offer is accepted"""
        message = (
            f"Your offer of {offer_amount} for {vehicle} has been accepted! "
            f"Complete payment within 24 hours. - Nzila Exports"
        )
        return self.send_sms(buyer_phone, message)
    
    def send_payment_due_notification(self, buyer_phone: str, vehicle: str, amount: str, deadline: str) -> bool:
        """Send notification when payment is due"""
        message = (
            f"Payment reminder: {amount} due by {deadline} for {vehicle}. "
            f"Pay now to secure your vehicle. - Nzila Exports"
        )
        return self.send_sms(buyer_phone, message)
    
    def send_shipment_departure_notification(
        self,
        buyer_phone: str,
        vehicle: str,
        port: str,
        eta: str,
        tracking: str
    ) -> bool:
        """Send notification when shipment departs"""
        message = (
            f"Your {vehicle} has departed for {port}! "
            f"ETA: {eta}. Track: {tracking}. - Nzila Exports"
        )
        return self.send_sms(buyer_phone, message)
    
    def send_inspection_appointment_reminder(
        self,
        buyer_phone: str,
        vehicle: str,
        appointment_time: str,
        dealer_address: str
    ) -> bool:
        """Send appointment reminder 24 hours before inspection"""
        message = (
            f"Reminder: Inspection for {vehicle} tomorrow at {appointment_time}. "
            f"Location: {dealer_address}. - Nzila Exports"
        )
        return self.send_sms(buyer_phone, message)
    
    def send_appointment_confirmed_notification(
        self,
        buyer_phone: str,
        vehicle: str,
        appointment_time: str,
        dealer_name: str
    ) -> bool:
        """Send notification when dealer confirms appointment"""
        message = (
            f"Your inspection for {vehicle} on {appointment_time} has been confirmed by {dealer_name}. "
            f"See you there! - Nzila Exports"
        )
        return self.send_sms(buyer_phone, message)
    
    def send_appointment_cancelled_notification(
        self,
        buyer_phone: str,
        vehicle: str,
        reason: Optional[str] = None
    ) -> bool:
        """Send notification when appointment is cancelled"""
        message = f"Your inspection for {vehicle} has been cancelled."
        if reason:
            message += f" Reason: {reason}."
        message += " Please book a new appointment. - Nzila Exports"
        return self.send_sms(buyer_phone, message)


# Global SMS service instance
sms_service = SMSService()
