from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view
from rest_framework.response import Response
from decimal import Decimal

from Furs_and_Coats_App.models import Product, Cart, CartItem
from Furs_and_Coats_App.services.RegService import RegService
from Furs_and_Coats_App.services.AuthService import AuthService


# Create your views here.


def index(request):
    # Если пользователь уже аутентифицирован, перенаправляем в каталог
    # if request.user.is_authenticated:
    #     return redirect('index.html')

    if request.method == 'POST':
        # Получение данных из формы
        login_identifier = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember', False)

        # Валидация данных
        validation_errors = AuthService.validate_login_data(login_identifier, password)

        if validation_errors:
            return render(request, "index.html", {
                'error_message': ' '.join(validation_errors),
                'login_identifier': login_identifier
            })

        # Попытка аутентификации
        try:
            user, profile = AuthService.authenticate_user(login_identifier, password)

            # Вход пользователя
            login(request, user)

            # Если выбрано "Запомнить меня", устанавливаем длинную сессию
            if remember_me:
                request.session.set_expiry(1209600)  # 2 недели
            else:
                request.session.set_expiry(0)  # Сессия до закрытия браузера

            # Успешная аутентификация - перенаправляем в каталог
            return redirect('catalog')

        except ValidationError as e:
            return render(request, "index.html", {
                'error_message': str(e),
                'login_identifier': login_identifier
            })
        except Exception as e:
            return render(request, "index.html", {
                'error_message': f'Произошла ошибка при входе: {str(e)}',
                'login_identifier': login_identifier
            })

    # GET запрос - отображение формы
    return render(request, "index.html")


def registration(request):
    if request.method == 'POST':
        # Получение данных из формы
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()

        # Сохранение данных формы для повторного отображения при ошибке
        form_data = {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
        }

        # Валидация данных
        validation_errors = RegService.validate_registration_data(
            username, email, password, confirm_password, first_name, last_name
        )

        if validation_errors:
            return render(request, "registration.html", {
                'error_message': ' '.join(validation_errors),
                'form_data': form_data
            })

        # Попытка регистрации
        try:
            user, profile = RegService.register_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone
            )

            # Успешная регистрация
            return render(request, "registration.html", {
                'success_message': f'Регистрация успешна! Добро пожаловать, {user.first_name}!'
            })

        except ValidationError as e:
            return render(request, "registration.html", {
                'error_message': str(e),
                'form_data': form_data
            })
        except Exception as e:
            return render(request, "registration.html", {
                'error_message': f'Произошла ошибка при регистрации: {str(e)}',
                'form_data': form_data
            })

    # GET запрос - отображение формы
    return render(request, "registration.html")


@login_required(login_url='/')
def catalog(request):
    products = Product.objects.all()
    return render(request, "catalog.html", {"products": products})


@login_required(login_url='/')
def cart(request):
    return render(request, "cart.html")


def logout_view(request):
    logout(request)
    return redirect('index')


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
