import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager

class CustomUser(AbstractUser):
    username = None
    phone_number = models.CharField(max_length=15, unique=True)
    user_bio = models.CharField(max_length=255, blank=True, null=True)
    user_profile = models.ImageField(upload_to='profile', blank=True, null=True)
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []
    
    objects = UserManager()
    
    def __str__(self):
        return self.phone_number

class BaseModel(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Product(BaseModel):
    MEASURING_CHOICES = (
        ('KG', 'Kilogram'),
        ('ML', 'Milliliter'),
        ('L', 'Liter'),
        ('PIECE', 'Piece'),
        ('NONE', 'None'),
    )
    
    product_name = models.CharField(max_length=200)
    product_slug = models.SlugField(unique=True)
    product_description = models.TextField()
    product_price = models.IntegerField()
    product_demo_price = models.IntegerField()
    quantity = models.CharField(max_length=50, null=True, blank=True)
    product_measuring = models.CharField(max_length=100, choices=MEASURING_CHOICES, default='NONE')
    
    def __str__(self):
        return self.product_name

class ProductMetaInformation(BaseModel):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='meta_information')
    product_measuring = models.CharField(max_length=100, choices=(('KG','KG'),('ML','Milliliter'),('None','None')))
    product_quantity = models.CharField(max_length=50, null=True, blank=True)
    is_restrict = models.BooleanField(default=False)
    restrict_quantity = models.IntegerField(default=0)

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
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
    )
    
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=15)
    customer_address = models.TextField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash_on_delivery')
    is_paid = models.BooleanField(default=False)
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
    
    def __str__(self):
        return f"{self.quantity}x {self.product.product_name}"
    
    @property
    def subtotal(self):
        return self.quantity * self.price 