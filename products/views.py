from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import (
    Product, Category, Order, ProductVariation, OrderItem, ProductImage, CustomUser,
    ProductAttribute, ProductAttributeValue, ProductVariant, ProductVariantAttributeValue
)
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.text import slugify
from django.db.models import Sum
from django.core.validators import  RegexValidator

# ============================================
# AUTHENTICATION VIEWS
# ===========================================
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

val_phoneNumber   = RegexValidator(
    regex=r'^(?:(?:(?:\+|00)92)|0)3[0-6]\d\d{7}$',
)

def register(request):
    val_pass = RegexValidator(
    regex=r'^(?=.*[a-z])(?=.*[A-Z]).{8,}$')
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('phone_number')
        try:
            val_phoneNumber(phone_number)
        except:
            messages.info(request, "Enter a valid Pakistani mobile number (e.g. 03011234567 or +923011234567)")
            return redirect('/register/')
        password = request.POST.get('password')
        try:
            val_pass(password)
        except:
            messages.info(request,"Password must be at least 8 characters long and contain at least one uppercase and one lowercase letter")
            return redirect('/register/')
        
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

# ============================================
# PUBLIC VIEWS
# ============================================

def home(request):
    latest_products = Product.objects.all().order_by('-created_at')[:3]
    total_products = Product.objects.count()
    
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(product_name__icontains=search_query)
    products_with_variations = []
    for product in latest_products:
        available_variations = product.variations.filter(is_available=True)
        products_with_variations.append({
            'product': product,
            'variations': available_variations,
            'has_variations': available_variations.exists()
        })
    context = {
        'latest_products': latest_products,
        'total_products': total_products,
        'products_with_variations': products_with_variations,  
        'search_query': search_query,
    }
    return render(request, 'user/home.html', context)

def menu(request):
    """Menu page with category filtering"""
    # Get all active categories
    categories = Category.objects.filter(is_active=True).order_by('display_order', 'category_name')
    
    # Get category filter from URL
    category_slug = request.GET.get('category')
    selected_category = None
    
    # Filter products
    products = Product.objects.filter(is_available=True)
    
    if category_slug:
        selected_category = get_object_or_404(Category, category_slug=category_slug, is_active=True)
        products = products.filter(category=selected_category)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(product_name__icontains=search_query)
        categories = categories.filter(category_name__icontains=search_query)
        categories
    
    # Calculate discount percentage for each product
    products_with_discount = []
    for product in products:
        discount_percentage = 0
        if product.product_demo_price > product.product_price:
            discount_percentage = round(((product.product_demo_price - product.product_price) / product.product_demo_price) * 100)
        
        # Check if product has variations
        has_variations = product.variations.filter(is_available=True).exists()
        
        products_with_discount.append({
            'product': product,
            'discount_percentage': discount_percentage,
            'has_variations': has_variations
        })
    
    context = {
        'categories': categories,
        'selected_category': selected_category,
        'products_with_discount': products_with_discount,
        'search_query': search_query
    }
    return render(request, 'user/Menu.html', context)

# ============================================
# CATEGORY MANAGEMENT VIEWS
# ============================================

@login_required
def manage_categories(request):
    """View and manage all categories"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied! Staff access required.')
        return redirect('home')
    
    categories = Category.objects.all().order_by('display_order', 'category_name')
    
    return render(request, 'restaurant/manage_categories.html', {
        'categories': categories
    })
@login_required
def add_category(request):
    """Add new category"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied! Staff access required.')
        return redirect('home')
    
    if request.method == 'POST':
        try:
            category_name = request.POST.get('category_name')
            category_description = request.POST.get('category_description', '')
            display_order = request.POST.get('display_order', 0)
            is_active = request.POST.get('is_active') == 'on'
            
            # Check if category already exists
            if Category.objects.filter(category_name__iexact=category_name).exists():
                messages.error(request, f'Category "{category_name}" already exists!')
                return redirect('manage_categories')
            
            # Create category
            category = Category.objects.create(
                category_name=category_name,
                category_slug=slugify(category_name),
                category_description=category_description,
                display_order=display_order,
                is_active=is_active
            )
            
            # Handle image upload
            if request.FILES.get('category_image'):
                category.category_image = request.FILES.get('category_image')
                category.save()
            
            messages.success(request, f'Category "{category_name}" added successfully!')
            return redirect('manage_categories')
            
        except Exception as e:
            messages.error(request, f' Error adding category: {str(e)}')
            return redirect('add_category')
    
    return render(request, 'restaurant/add_category.html')
@login_required
def edit_category(request, category_id):
    """Edit existing category"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied! Staff access required.')
        return redirect('home')
    
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        try:
            category.category_name = request.POST.get('category_name')
            category.category_description = request.POST.get('category_description', '')
            category.display_order = request.POST.get('display_order', 0)
            category.is_active = request.POST.get('is_active') == 'on'
            category.category_slug = slugify(category.category_name)
            
            # Handle image upload
            if request.FILES.get('category_image'):
                # Delete old image if exists
                if category.category_image:
                    category.category_image.delete(save=False)
                category.category_image = request.FILES.get('category_image')
            
            category.save()
            messages.success(request, f'Category "{category.category_name}" updated successfully!')
            return redirect('manage_categories')
            
        except Exception as e:
            messages.error(request, f'Error updating category: {str(e)}')
            return redirect('edit_category', category_id=category_id)
    
    return render(request, 'restaurant/edit_category.html', {'category': category})
@login_required
def delete_category(request, category_id):
    """Delete category"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied! Staff access required.')
        return redirect('home')
    
    category = get_object_or_404(Category, id=category_id)
    
    # Check if category has products
    product_count = category.products.count()
    
    if product_count > 0:
        messages.warning(request, 
            f' Cannot delete "{category.category_name}" - it has {product_count} product(s). '
            f'Please reassign or delete those products first.')
        return redirect('manage_categories')
    
    
    category_name = category.category_name
    category.delete()
    messages.success(request, f'Category "{category_name}" deleted successfully!')
    return redirect('manage_categories')
@login_required
def toggle_category_status(request, category_id):
    """Toggle category active/inactive status"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied! Staff access required.')
        return redirect('home')
    
    category = get_object_or_404(Category, id=category_id)
    category.is_active = not category.is_active
    category.save()
    
    status = "activated" if category.is_active else "deactivated"
    messages.success(request, f'Category "{category.category_name}" {status}!')
    return redirect('manage_categories')


def about(request):
    return render(request, 'user/about.html')

# ============================================
# CART VIEWS - COMPLETE WITH VARIATIONS
# ============================================

@login_required(login_url='/login/')
def cart_view(request):
    """Display cart with both regular products, variations, and variants"""
    cart = request.session.get('cart', {})
    cart_items = []
    total_amount = 0
    
    for cart_key, item_data in cart.items():
        try:
            # Check if it's a variant (new multi-attribute system)
            if 'variant_id' in item_data:
                # Cart item with variant
                variant = get_object_or_404(ProductVariant, id=item_data['variant_id'])
                product = variant.product
                quantity = item_data['quantity']
                item_total = variant.variant_price * quantity
                
                cart_items.append({
                    'cart_key': cart_key,
                    'product': product,
                    'variant': variant,
                    'variation': None,
                    'quantity': quantity,
                    'price': variant.variant_price,
                    'total_price': item_total,
                    'has_variant': True,
                    'has_variation': False
                })
                total_amount += item_total
            # Check if it's a variation (old simple variation system)
            elif 'variation_id' in item_data:
                # Cart item with variation
                variation = get_object_or_404(ProductVariation, id=item_data['variation_id'])
                product = variation.product
                quantity = item_data['quantity']
                item_total = variation.variation_price * quantity
                
                cart_items.append({
                    'cart_key': cart_key,
                    'product': product,
                    'variant': None,
                    'variation': variation,
                    'quantity': quantity,
                    'price': variation.variation_price,
                    'total_price': item_total,
                    'has_variant': False,
                    'has_variation': True
                })
                total_amount += item_total
            else:
                # Regular cart item without variation or variant
                product = get_object_or_404(Product, id=item_data['product_id'])
                quantity = item_data['quantity']
                item_total = product.product_price * quantity
                
                cart_items.append({
                    'cart_key': cart_key,
                    'product': product,
                    'variant': None,
                    'variation': None,
                    'quantity': quantity,
                    'price': product.product_price,
                    'total_price': item_total,
                    'has_variant': False,
                    'has_variation': False
                })
                total_amount += item_total
                
        except (Product.DoesNotExist, ProductVariation.DoesNotExist, ProductVariant.DoesNotExist):
            # Skip invalid items
            continue
    
    context = {
        'cart_items': cart_items,
        'total_amount': total_amount
    }
    return render(request, 'user/cart.html', context)

@login_required(login_url='/login/')
def add_to_cart(request, product_id):
    """Add regular product to cart (no variation)"""
    product = get_object_or_404(Product, id=product_id)
    
    # Check if product has variations - redirect to product detail
    if product.variations.filter(is_available=True).exists():
        messages.warning(request, f'{product.product_name} has size options. Please select a size.')
        return redirect('product_detail', product_slug=product.product_slug)
    
    cart = request.session.get('cart', {})
    cart_key = f"product_{product_id}"
    
    # Get quantity from query parameter (default 1)
    quantity = int(request.GET.get('quantity', 1))
    
    if cart_key in cart:
        cart[cart_key]['quantity'] += quantity
    else:
        cart[cart_key] = {
            'product_id': product_id,
            'quantity': quantity,
        }
    
    request.session['cart'] = cart
    request.session.modified = True
    
    # Check if "Buy Now" action
    buy_now = request.GET.get('buy_now', 'false') == 'true'
    
    if buy_now:
        messages.success(request, f'{product.product_name} added to cart!')
        return redirect('checkout')
    else:
        messages.success(request, f'{product.product_name} added to cart!')
        return redirect('menu')

@login_required(login_url='/login/')
def add_to_cart_with_variation(request, product_id, variation_id):
    """Add product with specific variation to cart"""
    product = get_object_or_404(Product, id=product_id)
    variation = get_object_or_404(ProductVariation, id=variation_id, product=product)
    
    if not variation.is_available:
        messages.error(request, f'{variation.variation_name} is currently unavailable.')
        return redirect('product_detail', product_slug=product.product_slug)
    
    cart = request.session.get('cart', {})
    cart_key = f"product_{product_id}_var_{variation_id}"
    
    # Get quantity from query parameter (default 1)
    quantity = int(request.GET.get('quantity', 1))
    
    if cart_key in cart:
        cart[cart_key]['quantity'] += quantity
    else:
        cart[cart_key] = {
            'product_id': product_id,
            'variation_id': variation_id,
            'quantity': quantity,
        }
    
    request.session['cart'] = cart
    request.session.modified = True
    
    # Check if "Buy Now" action
    buy_now = request.GET.get('buy_now', 'false') == 'true'
    
    if buy_now:
        messages.success(request, f'{product.product_name} ({variation.variation_name}) added to cart!')
        return redirect('checkout')
    else:
        messages.success(request, f'{product.product_name} ({variation.variation_name}) added to cart!')
        return redirect('menu')
    
@login_required(login_url='/login/')
def remove_from_cart(request, cart_key):
    """Remove item from cart"""
    cart = request.session.get('cart', {})
    
    if cart_key in cart:
        del cart[cart_key]
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, 'Item removed from cart!')
    
    return redirect('cart')

@login_required(login_url='/login/')
def update_cart_quantity(request, cart_key):
    """Update cart item quantity"""
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})
        
        if quantity > 0:
            if cart_key in cart:
                cart[cart_key]['quantity'] = quantity
        else:
            if cart_key in cart:
                del cart[cart_key]
        
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, 'Cart updated!')
    
    return redirect('cart')

# ============================================
# CHECKOUT VIEW - WITH VARIATIONS
# ============================================

@login_required(login_url='/login/')
def checkout(request):
    """Checkout page with variation support"""
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart')
    
    cart_items = []
    total_amount = 0
    
    # Process cart items
    for cart_key, item_data in cart.items():
        try:
            # Check if it's a variant (new multi-attribute system)
            if 'variant_id' in item_data:
                # Item with variant
                variant = get_object_or_404(ProductVariant, id=item_data['variant_id'])
                product = variant.product
                quantity = item_data['quantity']
                item_total = variant.variant_price * quantity
                
                cart_items.append({
                    'product': product,
                    'variant': variant,
                    'variation': None,
                    'quantity': quantity,
                    'price': variant.variant_price,
                    'total_price': item_total,
                    'has_variant': True,
                    'has_variation': False
                })
                total_amount += item_total
            # Check if it's a variation (old simple variation system)
            elif 'variation_id' in item_data:
                # Item with variation
                variation = get_object_or_404(ProductVariation, id=item_data['variation_id'])
                product = variation.product
                quantity = item_data['quantity']
                item_total = variation.variation_price * quantity
                
                cart_items.append({
                    'product': product,
                    'variant': None,
                    'variation': variation,
                    'quantity': quantity,
                    'price': variation.variation_price,
                    'total_price': item_total,
                    'has_variant': False,
                    'has_variation': True
                })
                total_amount += item_total
            else:
                # Regular item
                product = get_object_or_404(Product, id=item_data['product_id'])
                quantity = item_data['quantity']
                item_total = product.product_price * quantity
                
                cart_items.append({
                    'product': product,
                    'variant': None,
                    'variation': None,
                    'quantity': quantity,
                    'price': product.product_price,
                    'total_price': item_total,
                    'has_variant': False,
                    'has_variation': False
                })
                total_amount += item_total
                
        except (Product.DoesNotExist, ProductVariation.DoesNotExist, ProductVariant.DoesNotExist):
            continue
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone_number = request.POST.get('phone_number')
        try:
            val_phoneNumber(phone_number)
        except:
            messages.info(request, "Enter a valid Pakistani mobile number (e.g. 03011234567 or +923011234567)")
            return redirect('checkout')
        address = request.POST.get('address')
        notes = request.POST.get('notes', '')
        
        if not all([full_name, phone_number, address]):
            messages.error(request, 'Please fill all required fields!')
            return render(request, 'user/checkout.html', {
                'cart_items': cart_items,
                'total_amount': total_amount
            })
        
        # Create Order
        order = Order.objects.create(
            customer=request.user,
            customer_name=full_name,
            customer_phone=phone_number,
            customer_address=address,
            total_amount=total_amount,
            payment_method='cash_on_delivery',
            notes=notes,
            status='pending'
        )
        
        # Create OrderItems
        for cart_key, item_data in cart.items():
            try:
                # Handle variant (new multi-attribute system)
                if 'variant_id' in item_data:
                    variant = get_object_or_404(ProductVariant, id=item_data['variant_id'])
                    OrderItem.objects.create(
                        order=order,
                        product=variant.product,
                        quantity=item_data['quantity'],
                        price=variant.variant_price,
                        variation_name=variant.variant_name
                    )
                # Handle variation (old simple variation system)
                elif 'variation_id' in item_data:
                    # Order item with variation
                    variation = get_object_or_404(ProductVariation, id=item_data['variation_id'])
                    OrderItem.objects.create(
                        order=order,
                        product=variation.product,
                        quantity=item_data['quantity'],
                        price=variation.variation_price,
                        variation_name=variation.variation_name
                    )
                else:
                    # Regular order item
                    product = get_object_or_404(Product, id=item_data['product_id'])
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=item_data['quantity'],
                        price=product.product_price
                    )
            except:
                continue
        
        # Clear cart
        request.session['cart'] = {}
        request.session.modified = True
        
        messages.success(request, f'🎉 Order #{order.id} placed successfully!')
        return redirect('home')
    
    return render(request, 'user/checkout.html', {
        'cart_items': cart_items,
        'total_amount': total_amount
    })
# ============================================
# PRODUCT CRUD
# ============================================

@login_required
def manage_products(request):
    """View all products"""
    products = Product.objects.all()
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(product_name__icontains=search_query)
    
    context = {
        'products': products,
        'search_query': search_query,
    }
    return render(request, 'restaurant/manage_products.html', context)

@login_required
def add_product(request):
    """Add new product with variations"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied! Staff access required.')
        return redirect('home')
    
    categories = Category.objects.filter(is_active=True).order_by('display_order', 'category_name')
    
    if request.method == 'POST':
        try:
            # Get category
            category_id = request.POST.get('category')
            category = None
            if category_id:
                category = get_object_or_404(Category, id=category_id)
            
            # Check if it's a variable product
            is_variable = request.POST.get('is_variable') == 'on'
            
            # Create product
            product = Product.objects.create(
                category=category,
                product_name=request.POST.get('name'),
                product_slug=slugify(request.POST.get('name')),
                product_description=request.POST.get('description'),
                product_price=request.POST.get('price'),
                product_demo_price=request.POST.get('demo_price', request.POST.get('price')),
                quantity=request.POST.get('quantity'),
                product_measuring=request.POST.get('product_measuring', 'NONE'),
                is_variable=is_variable,
            )
            
            # Handle image upload
            if request.FILES.get('image'):
                ProductImage.objects.create(
                    product=product,
                    product_image=request.FILES.get('image')
                )
            
            if is_variable:
                # Handle attributes for variable products
                attribute_count = int(request.POST.get('attribute_count', 0))
                attributes_added = 0
                
                for i in range(1, attribute_count + 1):
                    attribute_name = request.POST.get(f'attribute_name_{i}')
                    is_primary = request.POST.get(f'is_primary_{i}') == 'on'
                    
                    if attribute_name:
                        # Create attribute
                        attribute = ProductAttribute.objects.create(
                            product=product,
                            name=attribute_name,
                            is_primary=is_primary,
                            display_order=i
                        )
                        
                        # Add attribute values
                        attribute_value_count = int(request.POST.get(f'attribute_value_count_{i}', 0))
                        for j in range(1, attribute_value_count + 1):
                            value_name = request.POST.get(f'attribute_value_{i}_{j}')
                            price_adjustment = request.POST.get(f'attribute_price_{i}_{j}', '0')
                            
                            if value_name:
                                # Safely convert price_adjustment to int
                                try:
                                    price_adj_value = int(price_adjustment) if price_adjustment else 0
                                except (ValueError, TypeError):
                                    price_adj_value = 0
                                
                                ProductAttributeValue.objects.create(
                                    attribute=attribute,
                                    value=value_name,
                                    price_adjustment=price_adj_value,
                                    display_order=j
                                )
                        
                        attributes_added += 1
                
                # Generate variants automatically
                if attributes_added > 0:
                    variants = product.generate_variants()
                    success_msg = f'Product "{product.product_name}" added successfully with {attributes_added} attribute(s) and {len(variants)} variant(s)!'
                else:
                    success_msg = f'Product "{product.product_name}" added successfully! Please add attributes in the admin panel.'
            else:
                # Handle simple variations if provided
                variation_count = int(request.POST.get('variation_count', 0))
                variations_added = 0
                
                for i in range(1, variation_count + 1):
                    variation_name = request.POST.get(f'variation_name_{i}')
                    variation_price = request.POST.get(f'variation_price_{i}')
                    variation_demo_price = request.POST.get(f'variation_demo_price_{i}')
                    is_available = request.POST.get(f'is_available_{i}') == 'on'
                    
                    # Only create variation if name and price are provided
                    if variation_name and variation_price:
                        ProductVariation.objects.create(
                            product=product,
                            variation_name=variation_name,
                            variation_price=variation_price,
                            variation_demo_price=variation_demo_price or variation_price,
                            is_available=is_available
                        )
                        variations_added += 1
                
                success_msg = f'Product "{product.product_name}" added successfully!'
                if variations_added > 0:
                    success_msg += f' {variations_added} variation(s) added.'
            
            messages.success(request, success_msg)
            return redirect('manage_products')
            
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')
            return redirect('add_product')
    
    return render(request, 'restaurant/add_product.html', {
        'measuring_choices': Product.MEASURING_CHOICES,
        'categories': categories
    })
@login_required
def edit_product(request, product_slug):
    """Edit existing product"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied! Staff access required.')
        return redirect('home')
    
    product = get_object_or_404(Product, product_slug=product_slug)
    categories = Category.objects.filter(is_active=True).order_by('display_order', 'category_name')
    
    if request.method == 'POST':
        try:
            # Update category
            category_id = request.POST.get('category')
            if category_id:
                product.category = get_object_or_404(Category, id=category_id)
            else:
                product.category = None
            
            # Update product fields
            product.product_name = request.POST.get('name')
            product.product_description = request.POST.get('description')
            product.product_price = request.POST.get('price')
            product.product_demo_price = request.POST.get('demo_price', product.product_price)
            product.quantity = request.POST.get('quantity')
            product.product_measuring = request.POST.get('product_measuring', 'NONE')
            product.product_slug = slugify(product.product_name)
            
            # Handle image upload
            if request.FILES.get('image'):
                # Delete old images
                product.images.all().delete()
                # Create new image
                ProductImage.objects.create(
                    product=product,
                    product_image=request.FILES.get('image')
                )
            
            product.save()
            messages.success(request, f'Product "{product.product_name}" updated successfully!')
            return redirect('manage_products')
            
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
            return redirect('edit_product', product_slug=product_slug)
    
    return render(request, 'restaurant/edit_product.html', {
        'product': product,
        'measuring_choices': Product.MEASURING_CHOICES,
        'categories': categories
    })
@login_required
def delete_product(request, product_slug):
    """Delete product"""
    product = get_object_or_404(Product, product_slug=product_slug)
    product.delete()
    messages.success(request, 'Product deleted successfully!')
    return redirect('manage_products')

# ============================================
# VARIATION CRUD
# ============================================

@login_required
def manage_variations(request, product_id):
    """Manage variations for a product"""
    product = get_object_or_404(Product, id=product_id)
    variations = product.variations.all().order_by('variation_price')
    return render(request, 'restaurant/manage_variations.html', {
        'product': product,
        'variations': variations
    })

@login_required
def add_variation(request, product_id):
    """Add new variation"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        ProductVariation.objects.create(
            product=product,
            variation_name=request.POST.get('variation_name'),
            variation_price=request.POST.get('variation_price'),
            variation_demo_price=request.POST.get('variation_demo_price') or request.POST.get('variation_price'),
            is_available=request.POST.get('is_available') == 'on'
        )
        messages.success(request, 'Variation added successfully!')
    
    return redirect('manage_products')

@login_required
def edit_variation(request, variation_id):
    """Edit variation"""
    variation = get_object_or_404(ProductVariation, id=variation_id)
    
    if request.method == 'POST':
        variation.variation_name = request.POST.get('variation_name')
        variation.variation_price = request.POST.get('variation_price')
        variation.variation_demo_price = request.POST.get('variation_demo_price') or variation.variation_price
        variation.is_available = request.POST.get('is_available') == 'on'
        variation.save()
        messages.success(request, 'Variation updated successfully!')
    
    return redirect('manage_products')

@login_required
def delete_variation(request, variation_id):
    """Delete variation"""
    variation = get_object_or_404(ProductVariation, id=variation_id)
    variation.delete()
    messages.success(request, 'Variation deleted successfully!')
    return redirect('manage_products')

# ============================================
# ORDER MANAGEMENT
# ============================================

@login_required(login_url='/login/')
def restaurant_dashboard(request):
    """Restaurant dashboard"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied! Staff access required.')
        return redirect('home')
    
    products = Product.objects.all()
    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    total_products = products.count()
    total_orders = Order.objects.count()
    pending_orders_count = Order.objects.filter(status='pending').count()
    total_revenue = Order.objects.filter(status='delivered').aggregate(total=Sum('total_amount'))['total'] or 0
    
    return render(request, 'restaurant/dashboard.html', {
        'products': products,
        'recent_orders': recent_orders,
        'total_products': total_products,
        'total_orders': total_orders,
        'pending_orders_count': pending_orders_count,
        'total_revenue': total_revenue,
    })
@login_required
def manage_orders(request):
    """Manage orders"""
    filter_status = request.GET.get('status', 'all')
    
    if filter_status == 'all':
        orders = Order.objects.all().order_by('-created_at')
    else:
        orders = Order.objects.filter(status=filter_status).order_by('-created_at')
    
    search_query = request.GET.get('search')
    if search_query:
        orders = orders.filter(id__icontains=search_query)
    return render(request, 'restaurant/manage_orders.html', {
        'orders': orders,
        'filter_status': filter_status,'search_query': search_query,
    })
@login_required
def update_order_status(request, order_id):
    """Update order status"""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated to {order.get_status_display()}!')
    
    return redirect('manage_orders')

@login_required(login_url='/login/')
def my_orders(request):
    """Customer orders page"""
    all_orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    
    current_orders = all_orders.filter(
        status__in=['pending', 'confirmed', 'preparing', 'on_delivery']
    )
    
    previous_orders = all_orders.filter(
        status__in=['delivered', 'cancelled']
    )
    
    return render(request, 'user/myorders.html', {
        'orders': all_orders,
        'current_orders': current_orders,
        'previous_orders': previous_orders,
    })
    
    
    
    
