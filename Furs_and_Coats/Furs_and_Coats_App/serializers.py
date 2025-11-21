from rest_framework import serializers

from Furs_and_Coats_App.models import Product


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "name", "description", "price", "category_name",
            "material", "size", "color", "in_stock", "image"
        ]