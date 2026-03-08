from django.http import JsonResponse
from django.shortcuts import render

def home(request):
    """Welcome page for Soil & Soul API"""
    return JsonResponse({
        'message': 'Welcome to Soil & Soul E-Commerce API',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'api': {
                'users': '/api/users/',
                'products': '/api/products/',
                'categories': '/api/products/categories/',
                'cart': '/api/cart/',
                'orders': '/api/orders/',
                'payments': '/api/payments/',
                'reviews': '/api/reviews/',
                'notifications': '/api/notifications/',
                'admin_panel': '/api/admin/',
            }
        },
        'documentation': 'See README.md for API documentation',
        'status': 'running'
    })
