from django.urls import path

from . import views
from .views import SalesReportView

urlpatterns = [
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('search/', views.search, name='search'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('cart/success/<int:order_id>/', views.success, name='success'),
    path('change_quantity/<str:product_id>/', views.change_quantity, name='change_quantity'),
    path('remove_from_cart/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('sales-report/', SalesReportView.as_view(), name='sales_report'),
    path('<slug:slug>/', views.category_detail, name='category_detail'),
    path('<slug:category_slug>/<slug:slug>/', views.product_detail, name='product_detail'),

    # Other URL patterns...
]
