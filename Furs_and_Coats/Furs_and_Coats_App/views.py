from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response


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
