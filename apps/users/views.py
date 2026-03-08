from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import UserProfile, Address, UserActivity
from .serializers import (
    UserSerializer, UserProfileSerializer, AddressSerializer, 
    UserRegistrationSerializer, UserActivitySerializer
)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """Create a new user account"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get current user profile"""
        profile = request.user.profile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)


class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['put'])
    def update_profile(self, request):
        """Update user profile"""
        profile = request.user.profile
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """Get default address"""
        try:
            address = Address.objects.get(user=request.user, is_default=True)
            serializer = self.get_serializer(address)
            return Response(serializer.data)
        except Address.DoesNotExist:
            return Response({"detail": "No default address set."}, status=status.HTTP_404_NOT_FOUND)


class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserActivity.objects.filter(user=self.request.user)
