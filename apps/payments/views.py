from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import stripe
import razorpay
import hmac
import hashlib
import json
from .models import Payment, Refund
from .serializers import PaymentSerializer, RefundSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY

# Initialize Razorpay client
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def create_payment(self, request):
        """Create and process payment"""
        order_id = request.data.get('order_id')
        payment_method = request.data.get('payment_method', 'credit_card')
        
        try:
            from apps.orders.models import Order
            order = Order.objects.get(id=order_id, user=request.user)
            
            payment, created = Payment.objects.get_or_create(
                order=order,
                defaults={
                    'user': request.user,
                    'amount': order.total_amount,
                    'payment_method': payment_method,
                }
            )
            
            # For COD, mark as completed
            if payment_method == 'cod':
                payment.status = 'completed'
                payment.save()
                order.status = 'confirmed'
                order.save()
            
            serializer = self.get_serializer(payment)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def process_stripe(self, request, pk=None):
        """Process Stripe payment"""
        payment = self.get_object()
        token = request.data.get('token')
        
        try:
            charge = stripe.Charge.create(
                amount=int(payment.amount * 100),
                currency='inr',
                source=token,
                description=f"Payment for {payment.order.order_number}"
            )
            
            payment.transaction_id = charge.id
            payment.status = 'completed'
            payment.gateway_response = charge
            payment.save()
            
            # Update order status
            payment.order.status = 'confirmed'
            payment.order.save()
            
            serializer = self.get_serializer(payment)
            return Response(serializer.data)
        except stripe.error.CardError as e:
            payment.status = 'failed'
            payment.save()
            return Response(
                {'detail': e.user_message},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def create_razorpay_order(self, request):
        """Create Razorpay order for UPI/Card payment"""
        order_id = request.data.get('order_id')
        payment_method = request.data.get('payment_method', 'upi')
        
        try:
            from apps.orders.models import Order
            order = Order.objects.get(id=order_id, user=request.user)
            
            # Create payment record
            payment, created = Payment.objects.get_or_create(
                order=order,
                defaults={
                    'user': request.user,
                    'amount': order.total_amount,
                    'payment_method': payment_method,
                    'status': 'pending',
                }
            )
            
            # Create Razorpay order
            razorpay_order = razorpay_client.order.create({
                'amount': int(order.total_amount * 100),  # Amount in paise
                'currency': 'INR',
                'receipt': str(order.order_number),
                'payment_capture': 1,
            })
            
            payment.gateway_response = {
                'razorpay_order_id': razorpay_order['id'],
                'amount': str(order.total_amount),
            }
            payment.save()
            
            return Response({
                'success': True,
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'amount': float(order.total_amount),
                'currency': 'INR',
                'customer_name': request.user.get_full_name() or request.user.username,
                'customer_email': request.user.email,
                'customer_contact': request.data.get('phone', ''),
                'payment_id': payment.id,
            })
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def verify_razorpay_payment(self, request):
        """Verify Razorpay payment signature"""
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_signature = request.data.get('razorpay_signature')
        payment_id = request.data.get('payment_id')
        
        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)
            
            # Verify payment signature
            body = f"{razorpay_order_id}|{razorpay_payment_id}"
            expected_signature = hmac.new(
                settings.RAZORPAY_KEY_SECRET.encode(),
                body.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if razorpay_signature == expected_signature:
                # Payment verified
                payment.transaction_id = razorpay_payment_id
                payment.status = 'completed'
                payment.gateway_response = {
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_payment_id': razorpay_payment_id,
                }
                payment.save()
                
                # Update order status
                payment.order.status = 'confirmed'
                payment.order.save()
                
                return Response({
                    'success': True,
                    'message': 'Payment verified successfully',
                    'transaction_id': razorpay_payment_id,
                })
            else:
                payment.status = 'failed'
                payment.save()
                return Response(
                    {'detail': 'Payment verification failed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Payment.DoesNotExist:
            return Response(
                {'detail': 'Payment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class RefundViewSet(viewsets.ModelViewSet):
    serializer_class = RefundSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Refund.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def request_refund(self, request):
        """Request refund for a payment"""
        payment_id = request.data.get('payment_id')
        reason = request.data.get('reason')
        
        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)
            
            refund, created = Refund.objects.get_or_create(
                payment=payment,
                defaults={
                    'user': request.user,
                    'reason': reason,
                    'amount': payment.amount,
                }
            )
            
            serializer = self.get_serializer(refund)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Payment.DoesNotExist:
            return Response(
                {'detail': 'Payment not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
