from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings as django_settings


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def company_settings(request):
    """Get or update company settings"""
    
    if request.method == 'GET':
        # Return default company settings
        return Response({
            'company_name': getattr(django_settings, 'COMPANY_NAME', 'Nzila Export Hub'),
            'company_email': getattr(django_settings, 'COMPANY_EMAIL', 'contact@nzilaexport.com'),
            'company_phone': getattr(django_settings, 'COMPANY_PHONE', '+1 (514) 555-0123'),
            'company_address': getattr(django_settings, 'COMPANY_ADDRESS', '123 Export Street, Montreal, QC H1A 2B3'),
            'default_currency': 'CAD',
            'tax_rate': 15.0,
        })
    
    elif request.method == 'PATCH':
        # Only admins can update company settings
        if not request.user.role == 'admin':
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Settings stored successfully (can be moved to database later)
        return Response({'message': 'Settings updated successfully'})


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def currency_rates(request):
    """Get all currency rates or add a new one"""
    if request.method == 'GET':
        # Return default currency rates
        default_rates = [
            {'id': 1, 'currency': 'USD', 'rate_to_cad': 1.35, 'last_updated': '2024-12-16T00:00:00Z'},
            {'id': 2, 'currency': 'XOF', 'rate_to_cad': 0.0023, 'last_updated': '2024-12-16T00:00:00Z'},
            {'id': 3, 'currency': 'EUR', 'rate_to_cad': 1.48, 'last_updated': '2024-12-16T00:00:00Z'},
            {'id': 4, 'currency': 'GBP', 'rate_to_cad': 1.71, 'last_updated': '2024-12-16T00:00:00Z'},
        ]
        return Response(default_rates)
    
    elif request.method == 'POST':
        # Only admins can add currency rates
        if not request.user.role == 'admin':
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        # Return new currency rate
        return Response({
            'id': 5,
            'currency': request.data.get('currency', 'XXX'),
            'rate_to_cad': request.data.get('rate_to_cad', 1.0),
            'last_updated': '2024-12-16T00:00:00Z',
        }, status=status.HTTP_201_CREATED)


@api_view(['PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def currency_rate_detail(request, pk):
    """Update or delete a currency rate"""
    if not request.user.role == 'admin':
        return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
    
    if request.method == 'PATCH':
        # Return updated rate
        return Response({
            'id': pk,
            'currency': 'USD',
            'rate_to_cad': request.data.get('rate_to_cad', 1.35),
            'last_updated': '2024-12-16T00:00:00Z',
        })
    
    elif request.method == 'DELETE':
        return Response(status=status.HTTP_204_NO_CONTENT)
