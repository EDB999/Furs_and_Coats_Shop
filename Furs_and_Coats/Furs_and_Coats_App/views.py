from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from Furs_and_Coats_App.models import Product


# Create your views here.


def index(request):
    return HttpResponse("Главная")


# Тестовые API endpoints для Swagger
@api_view(['GET'])
def api_overview(request):
    """
    Обзор доступных API endpoints
    """
    api_urls = {
        'message': 'Добро пожаловать в Furs and Coats API!',
        'endpoints': {
            'Swagger документация': '/swagger/',
            'ReDoc документация': '/redoc/',
            'Информация о пользователе': '/api/user-info/',
        }
    }
    return Response(api_urls)


@api_view(['GET'])
def user_info(request):
    """
    Получить информацию о пользователе
    """
    return Response({
        "user": {
            "id": 1,
            "username": "test_user",
            "email": "user@example.com"
        }
    })


@api_view(['GET'])
def product_list_api(request):
    products = Product.objects.all().select_related('category')

    products_data = []
    for product in products:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'category': product.category.name,
            'material': product.material,
            'size': product.size,
            'color': product.color,
            'in_stock': product.in_stock,
        })

    return Response({
        'count': len(products_data),
        'products': products_data
    })
