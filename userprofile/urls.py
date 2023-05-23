from django.contrib.auth import views as auth_views
from django.urls import path
from .views import GoogleAuthLoginView

from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('accounts/login/', GoogleAuthLoginView.as_view(), name='account_login'),
    path('login/', auth_views.LoginView.as_view(template_name='userprofile/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('myaccount/', views.myaccount, name='myaccount'),
    path('past-orders/', views.past_orders, name='past_orders'),
    path('past-orders/order-detail/<int:pk>', views.user_order_detail, name = 'user_order_detail'),
    path('my-store/', views.my_store, name='my_store'),
    path('my-store/order-detail/<int:pk>', views.my_store_order_detail, name='my_store_order_detail'),
    path('my-store/add-product/', views.add_product, name='add_product'),
    path('my-store/edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('my-store/delete-product/<int:pk>/', views.delete_product, name='delete_product'),
    path('vendors/<int:pk>/', views.vendor_detail, name='vendor_detail'),
    path('add_money/', views.add_money, name='add_money'),
    path('myaccount/edit_profile/', views.edit_profile, name='edit_profile'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
]
