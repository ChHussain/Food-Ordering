# 🍕 Food Ordering System

A full-featured Django-based web application for online food ordering with customer and restaurant management capabilities.

## 📋 Description

This Food Ordering System is a comprehensive web application that allows customers to browse menus, place orders, and track their delivery status. Restaurant administrators can manage products, categories, variations, and orders through an intuitive dashboard.

## ✨ Features

### Customer Features
- **User Authentication**: Register and login using phone number
- **Browse Menu**: View all available food items organized by categories
- **Product Details**: View detailed information about each product with multiple variations
- **Shopping Cart**: Add items to cart with quantity selection
- **Checkout**: Place orders with delivery address and contact information
- **Order Tracking**: View current and previous order history with status updates
- **Search**: Search for specific food items

### Restaurant/Admin Features
- **Dashboard**: Overview of orders, products, and revenue statistics
- **Product Management**: Add, edit, and delete products with images
- **Category Management**: Organize products into categories (Biryani, Fast Food, Beverages, etc.)
- **Product Variations**: Manage different sizes/quantities for products (e.g., 0.5 KG, 1 KG, Family Pack)
- **Order Management**: View and update order status (Pending, Confirmed, Preparing, On Delivery, Delivered, Cancelled)
- **Inventory Tracking**: Monitor stock quantities for product variations

## 🛠️ Technology Stack

- **Backend**: Django 5.2.8
- **Database**: SQLite3 (default, can be configured for PostgreSQL/MySQL)
- **Frontend**: HTML, CSS, JavaScript (Bootstrap for styling)
- **Authentication**: Custom User Model with phone number authentication
- **Media Storage**: Django's file storage system
- **Python Version**: 3.12+

## 📦 Installation

### Prerequisites
- Python 3.12 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/ChHussain/Food-Ordering.git
   cd Food-Ordering
   ```

2. **Create and activate virtual environment**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install django>=5.2,<5.3 pillow>=10.0
   ```
   
   Or create a `requirements.txt` file:
   ```
   Django>=5.2,<5.3
   Pillow>=10.0
   ```
   Then install with:
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (admin account)**
   ```bash
   python manage.py createsuperuser
   ```
   Note: You'll be prompted for a phone number (use Pakistani format: 03XXXXXXXXX) and password.

6. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/
   - Restaurant dashboard: http://127.0.0.1:8000/dashboard/

## 🚀 Usage

### For Customers

1. **Register**: Navigate to `/register/` and create an account with your phone number
2. **Browse Menu**: Visit `/menu/` to see all available products
3. **Add to Cart**: Select products and add them to your cart
4. **Checkout**: Proceed to checkout and enter delivery details
5. **Track Orders**: View your order status at `/my-orders/`

### For Restaurant Administrators

1. **Login**: Use your staff account to access the dashboard
2. **Manage Categories**: Add and organize product categories
3. **Add Products**: Create new products with images and variations
4. **Process Orders**: View incoming orders and update their status
5. **Monitor Performance**: Check dashboard statistics

## 📁 Project Structure

```
Food-Ordering/
├── foodordering/           # Main project configuration
│   ├── settings.py        # Django settings
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI configuration
├── products/              # Main application
│   ├── models.py          # Database models (Product, Order, Category, etc.)
│   ├── views.py           # View functions
│   ├── admin.py           # Admin configuration
│   ├── manager.py         # Custom user manager
│   ├── static/            # Static files (CSS, JS, images)
│   └── templates/         # HTML templates
│       ├── user/          # Customer-facing templates
│       └── restaurant/    # Admin dashboard templates
├── media/                 # Uploaded files (product images, category images)
├── db.sqlite3             # SQLite database
└── manage.py              # Django management script
```

## 🔧 Configuration

### Important Settings (settings.py)

- **SECRET_KEY**: Change this in production
- **DEBUG**: Set to `False` in production
- **ALLOWED_HOSTS**: Configure for your domain
- **DATABASES**: Configure for production database (PostgreSQL recommended)
- **MEDIA_ROOT** and **MEDIA_URL**: Configure for media file storage

### Authentication

The system uses a custom user model with phone number authentication:
- Username field: Phone number in Pakistani format (e.g., 03011234567 or +923011234567)
  - Pattern: `03XXXXXXXXX` (11 digits starting with 03) or `+923XXXXXXXXX` (with country code)
- Password validation: Minimum 8 characters with at least one uppercase and one lowercase letter

## 📊 Database Models

### Core Models
- **CustomUser**: Extended user model with phone number authentication
- **Category**: Product categories with images and display order
- **Product**: Food items with price, description, and category
- **ProductVariation**: Different sizes/quantities for products
- **ProductImage**: Product images (multiple per product)
- **Order**: Customer orders with status tracking
- **OrderItem**: Individual items in an order

## 🔒 Security Notes

⚠️ **Before deploying to production:**
1. Change `SECRET_KEY` in `settings.py`
2. Set `DEBUG = False`
3. Configure `ALLOWED_HOSTS`
4. Use environment variables for sensitive data
5. Use a production-grade database (PostgreSQL/MySQL)
6. Set up proper media file storage (AWS S3, etc.)
7. Configure HTTPS/SSL
8. Set up proper backup systems

## 📸 Screenshots

_Screenshots will be added here to showcase the application interface_

- Homepage
- Menu page with categories
- Product detail page
- Shopping cart
- Checkout process
- Order tracking
- Restaurant dashboard
- Product management

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some feature'`)
5. Push to the branch (`git push origin feature/your-feature-name`)
6. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 👨‍💻 Author

**ChHussain**
- GitHub: [@ChHussain](https://github.com/ChHussain)

## 📞 Support

For issues, questions, or suggestions, please open an issue on the GitHub repository.

## 🎯 Future Enhancements

- Payment gateway integration (Stripe, PayPal, etc.)
- Real-time order tracking with WebSockets
- SMS/Email notifications
- Customer reviews and ratings
- Discount coupons and promotions
- Multiple restaurant support
- Mobile application
- Analytics and reporting dashboard

---

Made with ❤️ using Django
