# MB Vogue E-Commerce Platform

A modern Django-based e-commerce platform tailored for the Nigerian market with Paystack payment integration.

## Features

### Customer Features
- **Product Catalog**: Browse products by category with search and filtering
- **Product Details**: View multiple images, select sizes and colors
- **Shopping Cart**: Add/remove items, update quantities
- **User Accounts**: Register, login, manage profiles
- **Checkout Process**: Secure checkout with shipping information
- **Payment Integration**: Paystack payment gateway integration
- **Order History**: Track past orders and their status

### Admin Panel Features
- **Custom Dashboard**: View sales statistics, revenue charts, and analytics
- **Product Management**: Add/edit products with multiple images and variants
- **Inventory Management**: Track stock levels with low stock alerts
- **Order Management**: View and update order statuses with bulk actions
- **Payment Tracking**: Monitor all transactions and their status
- **Customer Management**: View user profiles and order history

## Tech Stack

- **Backend**: Django 4.2.7
- **Database**: SQLite (development)
- **Payment**: Paystack
- **Frontend**: HTML, CSS, JavaScript with Bootstrap-like styling

## Installation

### Prerequisites
- Python 3.12+
- pip or uv package manager

### Setup Instructions

1. **Clone or navigate to the project directory**
   ```bash
   cd MB_vogue
   ```

2. **Install dependencies**
   ```bash
   # Using uv (recommended)
   uv sync

   # Or using pip
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env

   # Edit .env and add your actual Paystack keys
   # Get your keys from https://dashboard.paystack.co/
   PAYSTACK_SECRET_KEY=sk_test_your_actual_key_here
   PAYSTACK_PUBLIC_KEY=pk_test_your_actual_key_here
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create sample data (optional)**
   ```bash
   python manage.py create_sample_data
   ```

   This creates:
   - 6 product categories
   - 18 products with variants
   - Admin user (admin/admin123)
   - 5 sample customer accounts (customer1-5/password123)

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Frontend: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

## Default Login Credentials

### Admin Account
- **Username**: admin
- **Password**: admin123

### Customer Accounts
- **Username**: customer1, customer2, customer3, customer4, customer5
- **Password**: password123

## Project Structure

```
MB_vogue/
├── MB_vogue/           # Project settings
│   ├── settings.py     # Django configuration
│   ├── urls.py         # Main URL routing
│   └── admin.py        # Custom admin panel
├── core/               # Main app (products, cart, orders)
│   ├── models.py       # Product, Cart, Order models
│   ├── views.py        # Main views
│   ├── admin.py        # Admin configuration
│   └── management/     # Management commands
├── users/              # User authentication and profiles
│   ├── models.py       # UserProfile model
│   ├── views.py        # Auth views
│   └── forms.py        # User forms
├── payments/           # Payment processing
│   ├── models.py       # Payment model
│   └── views.py        # Paystack integration
├── templates/          # HTML templates
├── static/             # CSS, JavaScript, images
└── media/              # User-uploaded content
```

## Models

### Core Models
- **Category**: Product categories with images
- **Product**: Main product with pricing and availability
- **ProductVariant**: Size and color combinations with stock
- **ProductImage**: Multiple images per product
- **Cart/CartItem**: Shopping cart functionality
- **Order/OrderItem**: Order management

### User Models
- **User**: Django's built-in User model
- **UserProfile**: Extended user information

### Payment Models
- **Payment**: Paystack transaction records

## Admin Panel

The custom admin panel includes:
- **Dashboard**: Revenue statistics, recent orders, low stock alerts
- **Product Management**: Inline image and variant editing
- **Order Management**: Bulk status updates, filtering by date
- **Payment Tracking**: View all Paystack transactions

## Payment Integration

Uses Paystack for payment processing:
- Test mode by default
- Automatic payment verification
- Callback URL handling
- Transaction status tracking

## Security Notes

**Important**: Before deploying to production:
1. Set `DEBUG = False` in settings.py
2. Use environment variables for all sensitive data
3. Add your actual Paystack keys (test or live)
4. Set `ALLOWED_HOSTS` to your domain
5. Use a production database (PostgreSQL recommended)

## Development

### Running Tests
```bash
python manage.py test
```

### Creating New Products
1. Log in to the admin panel
2. Go to Core → Products
3. Click "Add Product"
4. Fill in product details
5. Add images and variants inline

### Management Commands
```bash
# Create sample data
python manage.py create_sample_data

# Create superuser
python manage.py createsuperuser

# Run migrations
python manage.py makemigrations
python manage.py migrate
```

## Deployment

For production deployment:
1. Set `DEBUG = False`
2. Configure `ALLOWED_HOSTS`
3. Use environment variables for secrets
4. Set up a production database
5. Configure static files serving
6. Use Gunicorn or uWSGI as WSGI server
7. Set up Nginx as reverse proxy
8. Configure HTTPS with SSL certificate

## License

This project is for educational and commercial use.

## Support

For issues and questions, please contact the development team.
