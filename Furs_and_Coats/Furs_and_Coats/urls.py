from django.contrib import admin
from django.urls import path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from Furs_and_Coats_App import views

schema_view = get_schema_view(
    openapi.Info(
        title="Furs and Coats API",
        default_version='v1',
        description="API for Furs and Coats project",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email=""),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny,],
)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('registration/', views.registration, name="registration"),
    path('catalog/', views.catalog, name="catalog"),
    path('', views.index, name="index"),
    path('logout/', views.logout_view, name="logout"),

    path('cart/', views.cart, name="cart"),
    path('api/cart/add/', views.add_to_cart, name='add-to-cart'),
    path('api/cart/update/', views.update_cart_item, name='update-cart-item'),
    path('api/cart/remove/', views.remove_from_cart, name='remove-from-cart'),
    path('api/cart/clear/', views.clear_cart, name='clear-cart'),

    # Тестовые API endpoints
    path('api/', views.api_overview, name='api-overview'),
    path('api/user-info/', views.user_info, name='user-info'),
    path('api/products/', views.product_list_api, name='product-list'),

    # Swagger документация
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]
