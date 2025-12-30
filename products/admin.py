from django.contrib import admin
from .models import CustomUser, Product, ProductMetaInformation, ProductImage, Order, OrderItem

# Register your models here.


admin.site.register(CustomUser)
admin.site.register(Product)
admin.site.register(ProductMetaInformation)
admin.site.register(ProductImage)
admin.site.register(Order)
admin.site.register(OrderItem)