from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Order
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.text import slugify  
from .models import *
# Create your views here.


def login_page(request):
    if request.method == "POST":
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        
        if not CustomUser.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Phone number not registered")
            return redirect('/login/')
        
        user = authenticate(request, username=phone_number, password=password)
        
        if user is None:
            messages.error(request, "Invalid password")
            return redirect('/login/')
        else:
            login(request, user)
            return redirect('/')
    
    return render(request, 'user/login.html')

def logout_page(request):
    logout(request)
    return redirect('/login/')

def register(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            messages.info(request, "Phone number already taken")
            return redirect('/register/')
        
        user = CustomUser.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
        )
        user.set_password(password)
        user.save()
        messages.info(request, "User registered successfully")
        return redirect('/login/')
    
    return render(request, 'user/signup.html')

def home(request):
  
    latest_products = Product.objects.all().order_by('-created_at')[:3]
    total_products = Product.objects.count()
    
    context = {
        'latest_products': latest_products,
        'total_products': total_products
    }
    return render(request, 'user/home.html', context)


def menu(request):
    products = Product.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(product_name__icontains=search_query)
    
    # Calculate discount percentage for each product
    products_with_discount = []
    for product in products:
        discount_percentage = 0
        if product.product_demo_price > product.product_price:
            discount_percentage = round(((product.product_demo_price - product.product_price) / product.product_demo_price) * 100)
        products_with_discount.append({
            'product': product,
            'discount_percentage': discount_percentage
        })
    
    context = {
        'products_with_discount': products_with_discount,
        'search_query': search_query
    }
    return render(request, 'user/Menu.html', context)

def about(request):
    return render(request,'user/about.html')
def contact(request):
    return render(request,'user/contact.html')
@login_required(login_url='/login/')
def cart_view(request):
    
    cart = request.session.get('cart', {})
    cart_items = []
    total_amount = 0
    
    for product_id, item_data in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            quantity = item_data['quantity']
            item_total = product.product_price * quantity
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total_price': item_total
            })
            total_amount += item_total
        except Product.DoesNotExist:
            continue
    
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount
    }
    return render(request, 'user/cart.html', context)
@login_required(login_url='/login/')
def add_to_cart(request, product_id):
    """Add item to cart"""
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1
    else:
        cart[product_id_str] = {
            'quantity': 1,
        }
    
    request.session['cart'] = cart
    request.session.modified = True
    messages.success(request, f'{product.product_name} added to cart!')
    return redirect('menu')
@login_required(login_url='/login/')
def remove_from_cart(request, product_id):
    """Remove item from cart"""
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)
    
    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, 'Item removed from cart!')
    
    return redirect('cart')
@login_required(login_url='/login/')
def update_cart_quantity(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        product_id_str = str(product_id)
        
        if quantity > 0:
            if product_id_str in cart:
                # Update the quantity in the dictionary
                cart[product_id_str]['quantity'] = quantity
        else:
            if product_id_str in cart:
                del cart[product_id_str]
        
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, 'Cart updated!')
    
    return redirect('cart')
@login_required(login_url='/login/')
def checkout(request):
    """Checkout page - Cash on Delivery only"""
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart')
    
    cart_items = []
    total_amount = 0
    
    # Fix: Handle cart dictionary structure
    for product_id, item_data in cart.items():
        try:
            product = get_object_or_404(Product, id=product_id)
            
            # Get quantity from dictionary
            if isinstance(item_data, dict):
                quantity = item_data.get('quantity', 1)
            else:
                quantity = item_data  # Fallback if it's stored as int
            
            item_total = product.product_price * quantity
            total_amount += item_total
            
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total_price': item_total
            })
        except Product.DoesNotExist:
            continue
    
    if request.method == 'POST':
        # Get form data
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        notes = request.POST.get('notes', '')
        
        # Validate required fields
        if not all([full_name, phone_number, address]):
            messages.error(request, 'Please fill all required fields!')
            context = {
                'cart_items': cart_items,
                'total_amount': total_amount
            }
            return render(request, 'user/checkout.html', context)
        
        # Create Order (Cash on Delivery only)
        order = Order.objects.create(
            customer=request.user if request.user.is_authenticated else None,
            customer_name=full_name,
            customer_phone=phone_number,
            customer_address=address,
            total_amount=total_amount,
            payment_method='cash_on_delivery',
            notes=notes,
            status='pending'
        )
        
        # Create OrderItems
        for product_id, item_data in cart.items():
            try:
                product = get_object_or_404(Product, id=product_id)
                
                # Get quantity from dictionary
                if isinstance(item_data, dict):
                    quantity = item_data.get('quantity', 1)
                else:
                    quantity = item_data
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=product.product_price
                )
            except Product.DoesNotExist:
                continue
        
        # Clear cart
        request.session['cart'] = {}
        request.session.modified = True
        
        messages.success(request, f'🎉 Order #{order.id} placed successfully! We will deliver in 30-45 minutes. Pay cash on delivery.')
        return redirect('home')
    
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount
    }
    return render(request, 'user/checkout.html', context)
def order_confirmation(request):
    return render(request, 'user/order_confirmation.html')
# Dashboard Views
@login_required(login_url='/login/')
def restaurant_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied!')
        return redirect('home')
    """Restaurant owner dashboard"""
    products = Product.objects.all()
    orders = Order.objects.all().order_by('-created_at')[:10]  # Last 10 orders
    total_products = products.count()
    total_orders = orders.count()
    
    context = {
        'products': products,
        'orders': orders,
        'total_products': total_products,
        'total_orders': total_orders,
    }
    return render(request, 'restaurant/dashboard.html', context)

@login_required
def manage_products(request):
    """View all products"""
    products = Product.objects.all()
    return render(request, 'restaurant/manage_products.html', {'products': products})

@login_required
def add_product(request):
    """Add new product"""
    if request.method == 'POST':
        product_name = request.POST.get('name')
        product_description = request.POST.get('description')
        product_price = request.POST.get('price')
        product_demo_price = request.POST.get('demo_price', product_price)
        quantity = request.POST.get('quantity')
        product_measuring = request.POST.get('product_measuring')
        image = request.FILES.get('image')
        
        # Generate slug from product name
        from django.utils.text import slugify
        product_slug = slugify(product_name)
        
        product = Product.objects.create(
            product_name=product_name,
            product_slug=product_slug,
            product_description=product_description,
            product_price=product_price,
            product_demo_price=product_demo_price,
            quantity=quantity,
            product_measuring=product_measuring
        )
        
        # Add product image
        if image:
            ProductImage.objects.create(product=product, product_image=image)
        
        messages.success(request, 'Product added successfully!')
        return redirect('manage_products')
    
    # Get measuring choices from model
    measuring_choices = Product.MEASURING_CHOICES
    
    return render(request, 'restaurant/add_product.html', {
        'measuring_choices': measuring_choices
    })
    
@login_required
def edit_product(request, product_id):
    """Edit existing product"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product.product_name = request.POST.get('name')
        product.product_description = request.POST.get('description')
        product.product_price = request.POST.get('price')
        product.product_demo_price = request.POST.get('demo_price', product.product_price)
        product.quantity = request.POST.get('quantity')
        product.product_measuring = request.POST.get('product_measuring')
        
        # Update slug if name changed
        product.product_slug = slugify(product.product_name)
        
        # Update image if new one is uploaded
        if request.FILES.get('image'):
            # Delete old images
            product.images.all().delete()
            # Add new image
            ProductImage.objects.create(product=product, product_image=request.FILES.get('image'))
        
        product.save()
        messages.success(request, 'Product updated successfully!')
        return redirect('manage_products')
    
    # Get measuring choices from model
    measuring_choices = Product.MEASURING_CHOICES
    
    return render(request, 'restaurant/edit_product.html', {
        'product': product,
        'measuring_choices': measuring_choices
    })
@login_required
def delete_product(request, product_id):

    product = get_object_or_404(Product, id=product_id)
    product.delete()
    return redirect('manage_products')


def manage_orders(request):
    """Admin view - all orders with filtering"""
  
    
    filter_status = request.GET.get('status', 'all')
    
    if filter_status == 'all':
        orders = Order.objects.all().order_by('-created_at')
    else:
        orders = Order.objects.filter(status=filter_status).order_by('-created_at')
    
    context = {
        'orders': orders,
        'filter_status': filter_status
    }
    return render(request, 'restaurant/manage_orders.html', context)

@login_required
def update_order_status(request, order_id):
    """Update order status"""
    # if not request.user.is_staff:
    #     messages.error(request, 'Access denied!')
    #     return redirect('home')
    
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated to {order.get_status_display()}')
        else:
            messages.error(request, 'Invalid status!')
    
    return redirect('manage_orders')
@login_required(login_url='/login/')
def my_orders(request):
    """Customer view - their own orders separated by status"""
    all_orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    
    # Current orders: pending, confirmed, preparing, on_delivery
    current_orders = all_orders.filter(
        status__in=['pending', 'confirmed', 'preparing', 'on_delivery']
    )
    
    # Previous orders: delivered, cancelled
    previous_orders = all_orders.filter(
        status__in=['delivered', 'cancelled']
    )
    
    context = {
        'orders': all_orders,
        'current_orders': current_orders,
        'previous_orders': previous_orders,
    }
    return render(request, 'user/myorders.html', context)