from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
import random
import re
from .models import UserProfile, Address, UserActivity, OTPVerification
from .serializers import (
    UserSerializer, UserProfileSerializer, AddressSerializer, 
    UserRegistrationSerializer, UserActivitySerializer
)


def send_sms_otp(phone_number):
    """Send OTP via Twilio Verify API"""
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        verification = client.verify \
            .v2 \
            .services(settings.TWILIO_VERIFY_SERVICE_SID) \
            .verifications \
            .create(to=phone_number, channel='sms')
        return verification.status == 'pending'
    except Exception as e:
        print(f"Twilio Verify send error: {e}")
        return False


def check_otp(phone_number, code):
    """Verify OTP via Twilio Verify API"""
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        verification_check = client.verify \
            .v2 \
            .services(settings.TWILIO_VERIFY_SERVICE_SID) \
            .verification_checks \
            .create(to=phone_number, code=code)
        return verification_check.status == 'approved'
    except Exception as e:
        print(f"Twilio Verify check error: {e}")
        return False

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action in ['login', 'register', 'send_otp', 'verify_otp']:
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['post'])
    def send_otp(self, request):
        """Send OTP to phone number via Twilio Verify"""
        phone_number = request.data.get('phone_number', '').strip()
        name = request.data.get('name', '').strip()

        if not phone_number:
            return Response({'detail': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Normalize: ensure +91 prefix for India
        if not phone_number.startswith('+'):
            phone_number = '+91' + phone_number.lstrip('0')

        if not re.match(r'^\+\d{10,15}$', phone_number):
            return Response({'detail': 'Invalid phone number'}, status=status.HTTP_400_BAD_REQUEST)

        # Store name for later use during verify
        OTPVerification.objects.filter(phone_number=phone_number, is_verified=False).delete()
        OTPVerification.objects.create(phone_number=phone_number, otp='000000', name=name)

        # Send OTP via Twilio Verify
        sent = send_sms_otp(phone_number)
        if not sent:
            return Response({'detail': 'Failed to send OTP. Try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'detail': 'OTP sent successfully'})

    @action(detail=False, methods=['post'])
    def verify_otp(self, request):
        """Verify OTP via Twilio Verify and create/login user"""
        phone_number = request.data.get('phone_number', '').strip()
        otp = request.data.get('otp', '').strip()

        if not phone_number.startswith('+'):
            phone_number = '+91' + phone_number.lstrip('0')

        # Verify OTP via Twilio Verify API
        if not check_otp(phone_number, otp):
            return Response({'detail': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)

        # Get stored name from OTPVerification record
        name = ''
        try:
            otp_record = OTPVerification.objects.filter(
                phone_number=phone_number,
                is_verified=False
            ).latest('created_at')
            name = otp_record.name or ''
            otp_record.is_verified = True
            otp_record.save()
        except OTPVerification.DoesNotExist:
            pass

        # Get or create user by phone number
        username = 'ph_' + phone_number.lstrip('+')
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_unusable_password()
            name_parts = name.split(' ', 1) if name else ['']
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            user.save()
            UserProfile.objects.get_or_create(
                user=user,
                defaults={'phone_number': phone_number}
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'is_new_user': created,
        })



    @action(detail=False, methods=['post'])
    def login(self, request):
        """Login and return JWT tokens"""
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(username=email, password=password)
        if not user:
            # Try finding user by email
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            })
        return Response({'detail': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
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
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
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
