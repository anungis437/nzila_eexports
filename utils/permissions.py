from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission class to restrict access to admin users only.
    Used for all admin dashboard API endpoints.
    """
    
    def has_permission(self, request, view):  # type: ignore[override]
        """Check if user is authenticated and has admin role"""
        return (
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) == 'admin'
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission class that allows:
    - Admins: full access (read + write)
    - Other authenticated users: read-only access
    - Unauthenticated users: no access
    """
    
    def has_permission(self, request, view):  # type: ignore[override]
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admin gets full access
        if getattr(request.user, 'role', None) == 'admin':
            return True
        
        # Others only get read access (GET, HEAD, OPTIONS)
        return request.method in permissions.SAFE_METHODS


class IsBrokerOrAdmin(permissions.BasePermission):
    """
    Permission class for broker-specific endpoints.
    Allows access to brokers (their own data) or admins (all data).
    """
    
    def has_permission(self, request, view):  # type: ignore[override]
        return (
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) in ['broker', 'admin']
        )
    
    def has_object_permission(self, request, view, obj):  # type: ignore[override]
        """Brokers can only access their own objects, admins can access all"""
        if getattr(request.user, 'role', None) == 'admin':
            return True
        
        # Check if object belongs to the broker
        if hasattr(obj, 'broker'):
            return obj.broker == request.user
        
        return False


class IsDealerOrAdmin(permissions.BasePermission):
    """
    Permission class for dealer-specific endpoints.
    Allows access to dealers (their own data) or admins (all data).
    """
    
    def has_permission(self, request, view):  # type: ignore[override]
        return (
            request.user and
            request.user.is_authenticated and
            getattr(request.user, 'role', None) in ['dealer', 'admin']
        )
    
    def has_object_permission(self, request, view, obj):  # type: ignore[override]
        """Dealers can only access their own objects, admins can access all"""
        if getattr(request.user, 'role', None) == 'admin':
            return True
        
        # Check if object belongs to the dealer
        if hasattr(obj, 'dealer'):
            return obj.dealer == request.user
        
        return False
