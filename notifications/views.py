from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q

from .models import Notification
from .serializers import NotificationSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_notifications(request):
    """
    List all notifications for the authenticated user.
    
    Query Parameters:
    - unread_only: boolean (default: false) - Return only unread notifications
    - limit: int (default: 50) - Maximum number of notifications to return
    - type: string - Filter by notification type
    """
    user = request.user
    
    # Start with user's notifications
    queryset = Notification.objects.filter(user=user)
    
    # Filter by unread status
    if request.GET.get('unread_only', '').lower() == 'true':
        queryset = queryset.filter(is_read=False)
    
    # Filter by type
    notification_type = request.GET.get('type')
    if notification_type:
        queryset = queryset.filter(type=notification_type)
    
    # Limit results
    limit = int(request.GET.get('limit', 50))
    queryset = queryset[:limit]
    
    serializer = NotificationSerializer(queryset, many=True)
    
    # Also return unread count
    unread_count = Notification.objects.filter(user=user, is_read=False).count()
    
    return Response({
        'notifications': serializer.data,
        'unread_count': unread_count
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, notification_id):
    """
    Mark a specific notification as read.
    """
    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.mark_as_read()
        
        serializer = NotificationSerializer(notification)
        return Response(serializer.data)
        
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    """
    Mark all notifications as read for the authenticated user.
    """
    user = request.user
    
    # Update all unread notifications
    updated_count = Notification.objects.filter(
        user=user,
        is_read=False
    ).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return Response({
        'success': True,
        'marked_read': updated_count
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notification(request, notification_id):
    """
    Delete a specific notification.
    """
    try:
        notification = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
        notification.delete()
        
        return Response({'success': True})
        
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_count(request):
    """
    Get the count of unread notifications for the authenticated user.
    """
    count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    
    return Response({'unread_count': count})
