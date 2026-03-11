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


def generate_otp():
    """Generate a random 6-digit OTP"""
    return str(random.randint(100000, 999999))


def send_sms_otp(phone_number, otp_code):
    """Send OTP via Fast2SMS Quick SMS API"""
    import requests as http_requests
    # Fast2SMS expects 10-digit Indian number without country code
    mobile = phone_number.lstrip('+')
    if mobile.startswith('91') and len(mobile) == 12:
        mobile = mobile[2:]
    url = 'https://www.fast2sms.com/dev/bulkV2'
    payload = {
        'route': 'q',
        'message': f'Your Soil & Soul Foods OTP is {otp_code}. Valid for 5 minutes. Do not share.',
        'flash': '0',
        'numbers': mobile,
    }
    headers = {
        'authorization': settings.FAST2SMS_API_KEY,
        'Content-Type': 'application/json',
        'cache-control': 'no-cache',
    }
    print(f"[Fast2SMS] Sending OTP={otp_code} to mobile={mobile}")
    response = http_requests.post(url, json=payload, headers=headers, timeout=30)
    print(f"[Fast2SMS] Response status={response.status_code}, body={response.text}")
    data = response.json()
    if data.get('return') is True:
        return True
    print(f"Fast2SMS error: {data}")
    msg = data.get('message', 'Failed to send OTP')
    if isinstance(msg, list):
        msg = msg[0]
    raise Exception(msg)

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
        """Send OTP to phone number via Fast2SMS"""
        phone_number = request.data.get('phone_number', '').strip()
        name = request.data.get('name', '').strip()

        if not phone_number:
            return Response({'detail': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Normalize: ensure +91 prefix for India
        if not phone_number.startswith('+'):
            phone_number = '+91' + phone_number.lstrip('0')

        if not re.match(r'^\+\d{10,15}$', phone_number):
            return Response({'detail': 'Invalid phone number'}, status=status.HTTP_400_BAD_REQUEST)

        # Generate OTP and store it
        otp_code = generate_otp()
        OTPVerification.objects.filter(phone_number=phone_number, is_verified=False).delete()
        OTPVerification.objects.create(phone_number=phone_number, otp=otp_code, name=name)

        # Send OTP via Fast2SMS
        try:
            sent = send_sms_otp(phone_number, otp_code)
            if not sent:
                return Response({'detail': 'Failed to send OTP. Try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'detail': f'OTP service error: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'detail': 'OTP sent successfully'})

    @action(detail=False, methods=['post'])
    def verify_otp(self, request):
        """Verify OTP and create/login user"""
        phone_number = request.data.get('phone_number', '').strip()
        otp = request.data.get('otp', '').strip()

        if not phone_number.startswith('+'):
            phone_number = '+91' + phone_number.lstrip('0')

        # Verify OTP against our stored record
        try:
            otp_record = OTPVerification.objects.filter(
                phone_number=phone_number,
                is_verified=False
            ).latest('created_at')
        except OTPVerification.DoesNotExist:
            return Response({'detail': 'No OTP found. Please request a new OTP.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if OTP matches
        if otp_record.otp != otp:
            return Response({'detail': 'Invalid or expired OTP'}, status=status.HTTP_400_BAD_REQUEST)

        # Mark as verified
        name = otp_record.name or ''
        otp_record.is_verified = True
        otp_record.save()

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
