from decimal import Decimal
from django.shortcuts import get_object_or_404
from Furs_and_Coats_App.models import Cart, CartItem, Product


class CartService:

    @staticmethod
    def get_user_cart(user):
        """Получить корзину пользователя"""
        cart, created = Cart.objects.get_or_create(user=user)
        return cart

    @staticmethod
    def get_cart_with_items(user):
        """Получить корзину с товарами и общей суммой"""
        cart = CartService.get_user_cart(user)
        cart_items = CartItem.objects.filter(cart=cart).select_related('product')

        total_amount = Decimal('0.00')
        for item in cart_items:
            total_amount += item.product.price * item.quantity

        return {
            'cart': cart,
            'cart_items': cart_items,
            'total_amount': total_amount
        }

    @staticmethod
    def add_to_cart(user, product_id):
        """Добавить товар в корзину"""
        product = get_object_or_404(Product, id=product_id)
        cart = CartService.get_user_cart(user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': 1}
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return cart_item

    @staticmethod
    def update_cart_item(user, cart_item_id, quantity):
        """Обновить количество товара в корзине"""
        if quantity < 1:
            raise ValueError('Количество должно бы хотя 1')

        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=user)
        cart_item.quantity = quantity
        cart_item.save()

        return cart_item

    @staticmethod
    def delete_from_cart(user, cart_item_id):
        """Удалить товар из корзины"""
        cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=user)
        cart_item.delete()
        return cart_item

    @staticmethod
    def clear_cart(user):
        """Очистить корзину"""
        cart = CartService.get_user_cart(user)
        CartItem.objects.filter(cart=cart).delete()
        return cart