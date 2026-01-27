
from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager
from django.utils.text import slugify

class CustomUser(AbstractUser):
    username = None
    phone_number = models.CharField(max_length=15, unique=True)
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    def __str__(self):
        return self.phone_number

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Category(BaseModel):
    """Product categories (e.g., Biryani, Fast Food, Beverages)"""
    category_name = models.CharField(max_length=100, unique=True)
    category_slug = models.SlugField(max_length=120, blank=True, unique=True)
    category_description = models.TextField(blank=True, null=True)
    category_image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0, help_text="Lower numbers appear first")
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['display_order', 'category_name']
    
    def save(self, *args, **kwargs):
        if not self.category_slug:
            self.category_slug = slugify(self.category_name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.category_name
    
    @property
    def product_count(self):
        """Count of products in this category"""
        return self.products.filter(is_available=True).count()

class Product(BaseModel):
    MEASURING_CHOICES = (
        ('KG', 'Kilogram'),
        ('ML', 'Milliliter'),
        ('L', 'Liter'),
        ('PIECE', 'Piece'),
        ('In','Inches'),
        ('NONE', 'None'),
    )
    
    # ✅ NEW: Add category field
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    
    product_name = models.CharField(max_length=200)
    product_slug = models.SlugField(max_length=250, blank=True)
    product_description = models.TextField()
    product_price = models.IntegerField()
    product_demo_price = models.IntegerField()
    quantity = models.CharField(max_length=50, null=True, blank=True)
    product_measuring = models.CharField(max_length=100, choices=MEASURING_CHOICES, default='NONE')
    is_available = models.BooleanField(default=True, help_text="Is product available for ordering?")
    is_variable = models.BooleanField(default=False, help_text="Is this a variable product with attributes?")
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from product name if blank"""
        if not self.product_slug:
            base_slug = slugify(self.product_name)
            self.product_slug = base_slug
            
            # Handle duplicate slugs (only if product exists in DB)
            if self.pk:
                counter = 1
                while Product.objects.filter(product_slug=self.product_slug).exclude(pk=self.pk).exists():
                    self.product_slug = f"{base_slug}-{counter}"
                    counter += 1
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.product_name

class ProductVariation(BaseModel):
    """Different size/quantity variations of a product (e.g., 0.5kg, 1kg, 1.5kg)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variations')
    variation_name = models.CharField(max_length=100, help_text="e.g., '0.5 KG', '1 KG', 'Large', 'Family Pack'")
    variation_price = models.IntegerField(help_text="Price for this variation")
    variation_demo_price = models.IntegerField(null=True, blank=True, help_text="Original price (for discount display)")
    is_available = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['variation_price']
        unique_together = ['product', 'variation_name']
    
    def __str__(self):
        return f"{self.product.product_name} - {self.variation_name}"
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage for this variation"""
        if self.variation_demo_price and self.variation_demo_price > self.variation_price:
            return round(((self.variation_demo_price - self.variation_price) / self.variation_demo_price) * 100)
        return 0

class ProductAttribute(BaseModel):
    """Attributes for variable products (e.g., Size, Crust Type, Toppings)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attributes')
    name = models.CharField(max_length=100, help_text="Attribute name (e.g., Size, Crust Type)")
    is_primary = models.BooleanField(default=False, help_text="Primary attribute controls base price")
    display_order = models.IntegerField(default=0, help_text="Display order for attributes")
    
    class Meta:
        ordering = ['display_order', 'name']
        unique_together = ['product', 'name']
    
    def __str__(self):
        return f"{self.product.product_name} - {self.name}"

class ProductAttributeValue(BaseModel):
    """Values for product attributes (e.g., Small, Medium, Large for Size)"""
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=100, help_text="Attribute value (e.g., Small, Medium, Large)")
    price_adjustment = models.IntegerField(default=0, help_text="Price adjustment for this value (only for primary attribute)")
    display_order = models.IntegerField(default=0, help_text="Display order for values")
    
    class Meta:
        ordering = ['display_order', 'value']
        unique_together = ['attribute', 'value']
    
    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

class ProductVariant(BaseModel):
    """Generated variants combining attribute values (e.g., Small + Thin Crust)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=100, unique=True, blank=True, help_text="Stock Keeping Unit")
    variant_price = models.IntegerField(help_text="Final price for this variant")
    variant_demo_price = models.IntegerField(null=True, blank=True, help_text="Original price (for discount display)")
    is_available = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['variant_price']
    
    def save(self, *args, **kwargs):
        """Auto-generate SKU if blank"""
        if not self.sku:
            # Generate SKU from product slug and variant attributes
            base_sku = f"{self.product.product_slug[:20]}"
            if self.pk:
                self.sku = f"{base_sku}-{self.pk}"
            else:
                # For new variants, use a temporary SKU
                import time
                self.sku = f"{base_sku}-{int(time.time())}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        attribute_values = self.attribute_values.all()
        if attribute_values:
            attrs = ", ".join([f"{av.attribute_value.attribute.name}: {av.attribute_value.value}" 
                              for av in attribute_values])
            return f"{self.product.product_name} ({attrs})"
        return f"{self.product.product_name} - Variant #{self.id}"
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage for this variant"""
        if self.variant_demo_price and self.variant_demo_price > self.variant_price:
            return round(((self.variant_demo_price - self.variant_price) / self.variant_demo_price) * 100)
        return 0
    
    @property
    def variant_name(self):
        """Human-readable name for the variant"""
        attribute_values = self.attribute_values.all()
        if attribute_values:
            return " - ".join([av.attribute_value.value for av in attribute_values])
        return f"Variant #{self.id}"

class ProductVariantAttributeValue(BaseModel):
    """Junction table connecting variants to their attribute values"""
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='attribute_values')
    attribute_value = models.ForeignKey(ProductAttributeValue, on_delete=models.CASCADE, related_name='variants')
    
    class Meta:
        unique_together = ['variant', 'attribute_value']
    
    def __str__(self):
        return f"{self.variant} - {self.attribute_value}"

class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    product_image = models.ImageField(upload_to='products')

# Order Model - Main order header
class Order(BaseModel):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('preparing', 'Preparing'),
        ('on_delivery', 'On Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_CHOICES = (
        ('cash_on_delivery', 'Cash on Delivery'),
    )
    
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=15)
    customer_address = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash_on_delivery')
    delivery_time = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"

# OrderItem Model - Individual items in an order
class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    variation_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.quantity}x {self.product.product_name}"
    
    @property
    def subtotal(self):
        return self.quantity * self.price