from django.contrib import admin
from django.urls import path
from products import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path('register/', views.register, name='register'),
    path('menu/', views.menu, name='menu'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('dashboard/', views.restaurant_dashboard, name='restaurant_dashboard'),
    path('dashboard/products/', views.manage_products, name='manage_products'),
    path('dashboard/products/add/', views.add_product, name='add_product'),
    path('dashboard/products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('dashboard/products/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('dashboard/orders/', views.manage_orders, name='manage_orders'),
    path('dashboard/orders/update/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('about/',views.about,name='about'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-confirmation/', views.order_confirmation, name='order_confirmation'),
    path('my-orders/', views.my_orders, name='my_orders'),

]


# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)