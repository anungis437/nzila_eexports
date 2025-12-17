"""
WhatsApp Business API Integration Service

This service provides integration with WhatsApp Business API for customer communication.
The service includes webhook handlers for incoming messages and methods for sending messages.

API Documentation: https://developers.facebook.com/docs/whatsapp/cloud-api
"""

import requests
import logging
import hmac
import hashlib
from typing import Dict, List, Optional
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class WhatsAppAPIError(Exception):
    """Custom exception for WhatsApp API errors."""
    pass


class WhatsAppService:
    """
    Service for interacting with WhatsApp Business API.
    
    Configuration required in settings.py:
    - WHATSAPP_API_TOKEN: Your WhatsApp Business API token
    - WHATSAPP_PHONE_NUMBER_ID: Your WhatsApp Business phone number ID
    - WHATSAPP_VERIFY_TOKEN: Token for webhook verification
    - WHATSAPP_API_URL: WhatsApp API base URL
    """
    
    def __init__(self):
        self.api_token = getattr(settings, 'WHATSAPP_API_TOKEN', None)
        self.phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', None)
        self.verify_token = getattr(settings, 'WHATSAPP_VERIFY_TOKEN', 'nzila_whatsapp_verify')
        self.api_url = getattr(settings, 'WHATSAPP_API_URL', 'https://graph.facebook.com/v18.0')
        self.enabled = bool(self.api_token and self.phone_number_id)
    
    def send_message(self, to: str, message: str, vehicle_id: Optional[int] = None) -> Dict:
        """
        Send WhatsApp message to a phone number.
        
        Args:
            to: Recipient phone number (with country code, e.g., +15555551234)
            message: Message text
            vehicle_id: Optional vehicle ID for context
            
        Returns:
            Dictionary with message ID and status
            
        Raises:
            WhatsAppAPIError: If API request fails
        """
        if not self.enabled:
            logger.warning("WhatsApp API not configured. Logging message instead.")
            return self._log_mock_message(to, message, vehicle_id)
        
        try:
            response = requests.post(
                f'{self.api_url}/{self.phone_number_id}/messages',
                headers={
                    'Authorization': f'Bearer {self.api_token}',
                    'Content-Type': 'application/json'
                },
                json={
                    'messaging_product': 'whatsapp',
                    'to': to,
                    'type': 'text',
                    'text': {'body': message}
                },
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"WhatsApp message sent to {to}: {result.get('messages', [{}])[0].get('id')}")
            
            return {
                'success': True,
                'message_id': result.get('messages', [{}])[0].get('id'),
                'status': 'sent'
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"WhatsApp API request failed: {str(e)}")
            raise WhatsAppAPIError(f"Failed to send WhatsApp message: {str(e)}")
    
    def send_template_message(self, to: str, template_name: str, 
                             language_code: str = 'en', parameters: Optional[List[str]] = None) -> Dict:
        """
        Send WhatsApp template message (pre-approved message).
        
        Args:
            to: Recipient phone number
            template_name: Name of approved template
            language_code: Template language (default: 'en')
            parameters: List of parameters to fill template placeholders
            
        Returns:
            Dictionary with message ID and status
        """
        if not self.enabled:
            logger.warning("WhatsApp API not configured. Logging template message.")
            return self._log_mock_message(to, f"Template: {template_name}", None)
        
        components = []
        if parameters:
            components.append({
                'type': 'body',
                'parameters': [{'type': 'text', 'text': param} for param in parameters]
            })
        
        try:
            response = requests.post(
                f'{self.api_url}/{self.phone_number_id}/messages',
                headers={
                    'Authorization': f'Bearer {self.api_token}',
                    'Content-Type': 'application/json'
                },
                json={
                    'messaging_product': 'whatsapp',
                    'to': to,
                    'type': 'template',
                    'template': {
                        'name': template_name,
                        'language': {'code': language_code},
                        'components': components
                    }
                },
                timeout=30
            )
            
            response.raise_for_status()
            result = response.json()
            
            return {
                'success': True,
                'message_id': result.get('messages', [{}])[0].get('id'),
                'status': 'sent'
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"WhatsApp template message failed: {str(e)}")
            raise WhatsAppAPIError(f"Failed to send template message: {str(e)}")
    
    def send_vehicle_inquiry(self, to: str, vehicle_data: Dict) -> Dict:
        """
        Send vehicle inquiry message with details.
        
        Args:
            to: Recipient phone number (dealer)
            vehicle_data: Dictionary with vehicle details
            
        Returns:
            Dictionary with message ID and status
        """
        message = self._format_vehicle_inquiry(vehicle_data)
        return self.send_message(to, message, vehicle_data.get('id'))
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """
        Verify WhatsApp webhook during setup.
        
        Args:
            mode: Verification mode from WhatsApp
            token: Verify token from WhatsApp
            challenge: Challenge string to echo back
            
        Returns:
            Challenge string if verified, None otherwise
        """
        if mode == 'subscribe' and token == self.verify_token:
            logger.info("WhatsApp webhook verified successfully")
            return challenge
        
        logger.warning(f"WhatsApp webhook verification failed: mode={mode}")
        return None
    
    def process_webhook(self, data: Dict) -> Dict:
        """
        Process incoming WhatsApp webhook message.
        
        Args:
            data: Webhook payload from WhatsApp
            
        Returns:
            Dictionary with processed message data
        """
        try:
            entry = data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            
            messages = value.get('messages', [])
            if not messages:
                return {'success': True, 'messages': []}
            
            processed = []
            for message in messages:
                processed_msg = {
                    'from': message.get('from'),
                    'id': message.get('id'),
                    'timestamp': message.get('timestamp'),
                    'type': message.get('type'),
                    'text': message.get('text', {}).get('body') if message.get('type') == 'text' else None
                }
                processed.append(processed_msg)
                
                # Log for debugging
                logger.info(f"Received WhatsApp message from {processed_msg['from']}: {processed_msg['text']}")
            
            return {
                'success': True,
                'messages': processed
            }
            
        except Exception as e:
            logger.error(f"Error processing WhatsApp webhook: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _format_vehicle_inquiry(self, vehicle_data: Dict) -> str:
        """Format vehicle inquiry message."""
        message = f"""New vehicle inquiry from Nzila Export Hub:

Vehicle: {vehicle_data.get('year')} {vehicle_data.get('make')} {vehicle_data.get('model')}
VIN: {vehicle_data.get('vin')}
Price: ${vehicle_data.get('price'):,.2f}
Mileage: {vehicle_data.get('mileage'):,} km

Customer is interested in this vehicle. Please respond at your earliest convenience.

View full details: https://nzila.com/vehicles/{vehicle_data.get('id')}
"""
        return message
    
    def _log_mock_message(self, to: str, message: str, vehicle_id: Optional[int]) -> Dict:
        """
        Log mock message when API is not configured.
        
        This allows development and testing without WhatsApp API access.
        """
        logger.info(f"[MOCK WhatsApp] To: {to}, Message: {message[:100]}..., Vehicle ID: {vehicle_id}")
        return {
            'success': True,
            'message_id': f'mock_{timezone.now().timestamp()}',
            'status': 'sent',
            'mock_data': True
        }
    
    def create_inquiry_template(self) -> Dict:
        """
        Create vehicle inquiry message template.
        
        This template needs to be approved by WhatsApp Business.
        Template name: 'vehicle_inquiry'
        """
        template_data = {
            'name': 'vehicle_inquiry',
            'language': 'en',
            'category': 'MARKETING',
            'components': [
                {
                    'type': 'BODY',
                    'text': 'New inquiry for your {{1}} {{2}} {{3}}. Customer is interested. View details: {{4}}'
                }
            ]
        }
        
        logger.info("Vehicle inquiry template structure created. Submit this to WhatsApp for approval.")
        return template_data


# Singleton instance
whatsapp_service = WhatsAppService()
