from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ValidationError
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from Furs_and_Coats_App.models import Product, Cart, CartItem, Category, Order, OrderItem
from Furs_and_Coats_App.serializers import ProductFilteredListSerializer, ProductCardSerializer, CategorySerializer, \
    CartSerializer, UpdateCartItemSerializer, AddToCartSerializer, DeleteCartItemSerializer, \
    OrderSerializer, CreateOrderSerializer
from Furs_and_Coats_App.services.CartService import CartService
from Furs_and_Coats_App.services.RegService import RegService
from Furs_and_Coats_App.services.AuthService import AuthService


def index(request):
    if request.method == 'POST':
        login_identifier = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember', False)

        validation_errors = AuthService.validate_login_data(login_identifier, password)

        if validation_errors:
            return render(request, "index.html", {
                'error_message': ' '.join(validation_errors),
                'login_identifier': login_identifier
            })

        try:
            user, profile = AuthService.authenticate_user(login_identifier, password)

            login(request, user)

            if remember_me:
                request.session.set_expiry(1209600)
            else:
                request.session.set_expiry(0)

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

    return render(request, "index.html")


def registration(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        phone = request.POST.get('phone', '').strip()

        form_data = {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
        }

        validation_errors = RegService.validate_registration_data(
            username, email, password, confirm_password, first_name, last_name
        )

        if validation_errors:
            return render(request, "registration.html", {
                'error_message': ' '.join(validation_errors),
                'form_data': form_data
            })

        try:
            user, profile = RegService.register_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone
            )

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

    return render(request, "registration.html")


@login_required(login_url='/')
def catalog(request):
    products = Product.objects.all()
    return render(request, "catalog.html", {"products": products})


@login_required(login_url='/')
def cart(request):
    cart_data = CartService.get_cart_with_items(request.user)

    context = {
        'cart_items': cart_data['cart_items'],
        'total_amount': cart_data['total_amount'],
    }
    return render(request, "cart.html", context)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request):
    try:
        cart_data = CartService.get_cart_with_items(request.user)
        serializer = CartSerializer(cart_data['cart'])
        return Response(serializer.data)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    try:
        serializer = AddToCartSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            cart_item = CartService.add_to_cart(request.user, product_id)

            cart_data = CartService.get_cart_with_items(request.user)
            cart_serializer = CartSerializer(cart_data['cart'])

            return Response({
                "success": True,
                "message": "Товар добавлен в корзину",
                "quantity": cart_item.quantity,
                "cart": cart_serializer.data
            })
        else:
            return Response({"success": False, "error": serializer.errors}, status=400)

    except Product.DoesNotExist:
        return Response({"success": False, "error": "Product not found"}, status=404)
    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=500)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, cart_item_id):
    try:
        serializer = UpdateCartItemSerializer(data=request.data)
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            cart_item = CartService.update_cart_item(request.user, cart_item_id, quantity)

            cart_data = CartService.get_cart_with_items(request.user)
            cart_serializer = CartSerializer(cart_data['cart'])

            item_total = cart_item.product.price * cart_item.quantity

            return Response({
                "success": True,
                "quantity": cart_item.quantity,
                "item_total": str(item_total),
                "total_amount": str(cart_data['total_amount']),
                "cart": cart_serializer.data
            })
        else:
            return Response({"success": False, "error": serializer.errors}, status=400)

    except ValueError as e:
        return Response({"success": False, "error": str(e)}, status=400)
    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_from_cart(request, cart_item_id):
    try:
        cart_item = CartService.delete_from_cart(request.user, cart_item_id)

        cart_data = CartService.get_cart_with_items(request.user)
        cart_serializer = CartSerializer(cart_data['cart'])

        return Response({
            "success": True,
            "total_amount": str(cart_data['total_amount']),
            "cart": cart_serializer.data
        })

    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=500)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    try:
        CartService.clear_cart(request.user)

        cart_data = CartService.get_cart_with_items(request.user)
        cart_serializer = CartSerializer(cart_data['cart'])

        return Response({
            "success": True,
            "message": "Корзина очищена",
            "cart": cart_serializer.data
        })

    except Exception as e:
        return Response({"success": False, "error": str(e)}, status=500)


@swagger_auto_schema(
    method='get',
    operation_description="Получить корзину текущего пользователя в формате JSON. Пользователь может получить только свою корзину.",
    responses={
        200: openapi.Response(
            description="Корзина успешно получена",
            schema=CartSerializer
        ),
        401: openapi.Response(description="Пользователь не аутентифицирован"),
    },
    tags=['Cart']
)
@swagger_auto_schema(
    method='post',
    operation_description="Добавить товар в корзину. Требуется указать product_id в теле запроса.",
    request_body=AddToCartSerializer,
    responses={
        200: openapi.Response(
            description="Товар успешно добавлен в корзину",
            examples={
                "application/json": {
                    "success": True,
                    "message": "Товар добавлен в корзину",
                    "quantity": 1,
                    "cart": {
                        "id": 1,
                        "items": [],
                        "total_amount": "1000.00"
                    }
                }
            }
        ),
        400: openapi.Response(description="Ошибка валидации данных"),
        401: openapi.Response(description="Пользователь не аутентифицирован"),
        404: openapi.Response(description="Товар не найден"),
    },
    tags=['Cart']
)
@swagger_auto_schema(
    method='put',
    operation_description="Обновить количество товара в корзине. Требуется указать cart_item_id и quantity в теле запроса.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'cart_item_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID товара в корзине'),
            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='Новое количество товара (минимум 1)'),
        },
        required=['cart_item_id', 'quantity']
    ),
    responses={
        200: openapi.Response(
            description="Количество товара успешно обновлено",
            examples={
                "application/json": {
                    "success": True,
                    "quantity": 2,
                    "item_total": "2000.00",
                    "total_amount": "2000.00",
                    "cart": {}
                }
            }
        ),
        400: openapi.Response(description="Ошибка валидации данных"),
        401: openapi.Response(description="Пользователь не аутентифицирован"),
        404: openapi.Response(description="Товар в корзине не найден"),
    },
    tags=['Cart']
)
@swagger_auto_schema(
    method='delete',
    operation_description="Удалить товар из корзины или очистить корзину полностью. "
                          "Если указан cart_item_id - удаляется конкретный товар, "
                          "если cart_item_id не указан - очищается вся корзина.",
    request_body=DeleteCartItemSerializer,
    responses={
        200: openapi.Response(
            description="Товар успешно удален или корзина очищена",
            examples={
                "application/json": {
                    "success": True,
                    "message": "Товар удален из корзины",
                    "total_amount": "0.00",
                    "cart": {}
                }
            }
        ),
        401: openapi.Response(description="Пользователь не аутентифицирован"),
        404: openapi.Response(description="Товар в корзине не найден"),
    },
    tags=['Cart']
)
@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_api(request):
    try:
        if request.method == 'GET':
            cart_data = CartService.get_cart_with_items(request.user)
            serializer = CartSerializer(cart_data['cart'])
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'POST':
            serializer = AddToCartSerializer(data=request.data)
            if serializer.is_valid():
                product_id = serializer.validated_data['product_id']
                cart_item = CartService.add_to_cart(request.user, product_id)

                cart_data = CartService.get_cart_with_items(request.user)
                cart_serializer = CartSerializer(cart_data['cart'])

                return Response({
                    "success": True,
                    "message": "Товар добавлен в корзину",
                    "quantity": cart_item.quantity,
                    "cart": cart_serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "success": False,
                    "error": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'PUT':
            cart_item_id = request.data.get('cart_item_id')
            quantity = request.data.get('quantity')

            if not cart_item_id:
                return Response({
                    "success": False,
                    "error": "cart_item_id обязателен для обновления товара"
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer = UpdateCartItemSerializer(data={'quantity': quantity})
            if serializer.is_valid():
                quantity = serializer.validated_data['quantity']
                cart_item = CartService.update_cart_item(request.user, cart_item_id, quantity)

                cart_data = CartService.get_cart_with_items(request.user)
                cart_serializer = CartSerializer(cart_data['cart'])

                item_total = cart_item.product.price * cart_item.quantity

                return Response({
                    "success": True,
                    "quantity": cart_item.quantity,
                    "item_total": str(item_total),
                    "total_amount": str(cart_data['total_amount']),
                    "cart": cart_serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "success": False,
                    "error": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            cart_item_id = request.data.get('cart_item_id')

            if cart_item_id:
                cart_item = CartService.delete_from_cart(request.user, cart_item_id)

                cart_data = CartService.get_cart_with_items(request.user)
                cart_serializer = CartSerializer(cart_data['cart'])

                return Response({
                    "success": True,
                    "message": "Товар удален из корзины",
                    "total_amount": str(cart_data['total_amount']),
                    "cart": cart_serializer.data
                }, status=status.HTTP_200_OK)
            else:
                CartService.clear_cart(request.user)

                cart_data = CartService.get_cart_with_items(request.user)
                cart_serializer = CartSerializer(cart_data['cart'])

                return Response({
                    "success": True,
                    "message": "Корзина очищена",
                    "cart": cart_serializer.data
                }, status=status.HTTP_200_OK)

    except Product.DoesNotExist:
        return Response({
            "success": False,
            "error": "Товар не найден"
        }, status=status.HTTP_404_NOT_FOUND)
    except ValueError as e:
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def logout_view(request):
    logout(request)
    return redirect('index')


@swagger_auto_schema(
    method='post',
    operation_description="Создать заказ из товаров в корзине пользователя. "
                          "После успешного создания заказа корзина будет автоматически очищена. "
                          "Тело запроса может быть пустым - заказ создается из текущей корзины.",
    request_body=CreateOrderSerializer,
    responses={
        201: openapi.Response(
            description="Заказ успешно создан",
            schema=OrderSerializer,
            examples={
                "application/json": {
                    "success": True,
                    "message": "Заказ успешно создан",
                    "order": {
                        "id": 1,
                        "user": 1,
                        "status": "pending",
                        "status_display": "Ожидает обработки",
                        "total_amount": "50000.00",
                        "created_at": "2024-01-15T10:30:00Z",
                        "items": [
                            {
                                "id": 1,
                                "product_id": 1,
                                "product_name": "Шуба норковая",
                                "quantity": 2,
                                "price": "50000.00"
                            }
                        ]
                    }
                }
            }
        ),
        400: openapi.Response(description="Корзина пуста или ошибка валидации"),
        401: openapi.Response(description="Пользователь не аутентифицирован"),
    },
    tags=['Order']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    try:
        cart_data = CartService.get_cart_with_items(request.user)
        cart_items = cart_data['cart_items']
        total_amount = cart_data['total_amount']

        if not cart_items.exists():
            return Response({
                "success": False,
                "error": "Корзина пуста. Невозможно создать заказ из пустой корзины."
            }, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            user=request.user,
            status='pending',
            total_amount=total_amount
        )

        order_items = []
        for cart_item in cart_items:
            order_item = OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            order_items.append(order_item)

        CartService.clear_cart(request.user)

        serializer = OrderSerializer(order)

        return Response({
            "success": True,
            "message": "Заказ успешно создан",
            "order": serializer.data
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            "success": False,
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def get_products_by_filter(request):
    try:
        products = Product.objects.all()

        category_id = request.GET.get('category')
        if category_id:
            products = products.filter(category_id=category_id)

        min_price = request.GET.get('min_price')
        if min_price:
            products = products.filter(price__gte=min_price)

        max_price = request.GET.get('max_price')
        if max_price:
            products = products.filter(price__lte=max_price)

        sort = request.GET.get('sort')
        if sort == 'price_asc':
            products = products.order_by('price')
        elif sort == 'price_desc':
            products = products.order_by('-price')
        else:
            products = products.order_by('id')

        serializer = ProductFilteredListSerializer(products, many=True)

        return Response({
            "filters_applied": {
                "category": category_id,
                "min_price": min_price,
                "max_price": max_price,
                "sort": sort
            },
            "products_count": products.count(),
            "products": serializer.data
        })

    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(['GET'])
def get_product_card(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    serializer = ProductCardSerializer(product)

    return Response(serializer.data)


@api_view(['GET'])
def get_categories(request):
    categories = Category.objects.all()

    serializer = CategorySerializer(categories, many=True)

    return Response(serializer.data)


@api_view(['GET'])
def api_overview(request):
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
