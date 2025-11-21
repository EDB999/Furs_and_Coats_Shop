from rest_framework import serializers

from Furs_and_Coats_App.models import Product, Category


class ProductFilteredListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка товаров (меньше данных)"""
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category', 'category_name',
                  'image']


class ProductCardSerializer(serializers.ModelSerializer):
    """Сериализатор для детальной карточки товара (все данные)"""

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category',
                  'material', 'size', 'color', 'in_stock', 'image']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']
