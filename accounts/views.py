from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, UserProfileSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """Get or update current user profile"""
        if request.method == 'GET':
            serializer = UserProfileSerializer(request.user)
            return Response(serializer.data)
        else:
            serializer = UserProfileSerializer(
                request.user,
                data=request.data,
                partial=request.method == 'PATCH'
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
