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
    
    
    
    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/add-variation/<int:product_id>/<int:variation_id>/', views.add_to_cart_with_variation, name='add_to_cart_with_variation'),
    path('cart/remove/<str:cart_key>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<str:cart_key>/', views.update_cart_quantity, name='update_cart_quantity'),
    
    # Dashboard
    path('dashboard/', views.restaurant_dashboard, name='restaurant_dashboard'),
    path('dashboard/products/', views.manage_products, name='manage_products'),
    path('dashboard/products/add/', views.add_product, name='add_product'),
    path('dashboard/products/edit/<slug:product_slug>/', views.edit_product, name='edit_product'),
    path('dashboard/products/delete/<slug:product_slug>/', views.delete_product, name='delete_product'),
    path('dashboard/categories/', views.manage_categories, name='manage_categories'),
    path('dashboard/categories/add/', views.add_category, name='add_category'),
    path('dashboard/categories/edit/<int:category_id>/', views.edit_category, name='edit_category'),
    path('dashboard/categories/delete/<int:category_id>/', views.delete_category, name='delete_category'),
    path('dashboard/categories/toggle/<int:category_id>/', views.toggle_category_status, name='toggle_category_status'),

    
    path('dashboard/products/<int:product_id>/variations/', views.manage_variations, name='manage_variations'),
    path('dashboard/products/<int:product_id>/variations/add/', views.add_variation, name='add_variation'),
    path('dashboard/variations/<int:variation_id>/edit/', views.edit_variation, name='edit_variation'),
    path('dashboard/variations/<int:variation_id>/delete/', views.delete_variation, name='delete_variation'),
    
    path('dashboard/orders/', views.manage_orders, name='manage_orders'),
    path('dashboard/orders/update/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('about/', views.about, name='about'),
    path('checkout/', views.checkout, name='checkout'),
    path('my-orders/', views.my_orders, name='my_orders'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)