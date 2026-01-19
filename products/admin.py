from django.contrib import admin
from .models import CustomUser, Product, ProductImage, ProductVariation, Category, Order, OrderItem

# CustomUser Admin
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined']
    list_filter = ['is_staff', 'is_active', 'date_joined']
    search_fields = ['phone_number', 'first_name', 'last_name']
    ordering = ['-date_joined']

# Product Image Inline
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

# Product Variation Inline
class ProductVariationInline(admin.TabularInline):
    model = ProductVariation
    extra = 1
    fields = ['variation_name', 'variation_price', 'variation_demo_price', 'is_available']

# Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'product_name', 
        'category',  # ✅ Keep this
        'product_price', 
        'is_available',  # ✅ Keep this
        # ❌ REMOVED: 'is_featured'
        'created_at'
    ]
    list_filter = [
        'category', 
        'is_available',  # ✅ Keep this
        # ❌ REMOVED: 'is_featured'
        'created_at'
    ]
    search_fields = ['product_name', 'product_description']
    prepopulated_fields = {'product_slug': ('product_name',)}
    list_editable = [
        'is_available',  # ✅ Keep this
        # ❌ REMOVED: 'is_featured'
    ]
    inlines = [ProductImageInline, ProductVariationInline]
    ordering = ['-created_at']

# Category Admin
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name', 'is_active', 'display_order', 'product_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['category_name', 'category_description']
    prepopulated_fields = {'category_slug': ('category_name',)}
    list_editable = ['is_active', 'display_order']
    ordering = ['display_order', 'category_name']

# Order Item Inline
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'variation_name', 'quantity', 'price', 'subtotal']
    can_delete = False

# Order Admin
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 
        'customer_name', 
        'customer_phone', 
        'total_amount', 
        'status', 
        'payment_method',
        'created_at'
    ]
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['customer_name', 'customer_phone', 'customer_address']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderItemInline]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('customer', 'customer_name', 'customer_phone', 'customer_address')
        }),
        ('Order Details', {
            'fields': ('total_amount', 'status', 'payment_method', 'delivery_time', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Product Variation Admin
@admin.register(ProductVariation)
class ProductVariationAdmin(admin.ModelAdmin):
    list_display = [
        'product', 
        'variation_name', 
        'variation_price', 
        'is_available',
        'discount_percentage'
    ]
    list_filter = ['is_available', 'product']
    search_fields = ['product__product_name', 'variation_name']
    list_editable = ['is_available']
    ordering = ['product', 'variation_price']

# Product Image Admin (optional, usually managed via Product inline)
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'product_image', 'created_at']
    list_filter = ['created_at']
    search_fields = ['product__product_name']