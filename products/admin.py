from django.contrib import admin
from .models import CustomUser, Product, ProductVariation, ProductImage, Order, OrderItem, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name', 'product_count', 'is_active', 'display_order', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['category_name', 'category_description']
    prepopulated_fields = {'category_slug': ('category_name',)}
    list_editable = ['is_active', 'display_order']

class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1
    fields = ['variation_name', 'variation_price', 'variation_demo_price', 'stock_quantity', 'is_available']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'category', 'product_price', 'is_available', 'is_featured', 'created_at']
    list_filter = ['category', 'is_available', 'is_featured', 'product_measuring']
    search_fields = ['product_name', 'product_description']
    prepopulated_fields = {'product_slug': ('product_name',)}
    list_editable = ['is_available', 'is_featured']
    inlines = [ProductVariationInline]

admin.site.register(CustomUser)
admin.site.register(ProductImage)
admin.site.register(Order)
admin.site.register(OrderItem)