from flask import Blueprint, render_template, flash, redirect, request, jsonify, url_for, send_file
from .models import Product, Cart, Order, Wishlist, Review, Customer
from flask_login import login_required, current_user
from . import db
import io
from sqlalchemy import func
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_mail import Message
from flask_login import login_required, current_user
from . import mail, db
import random
import os
from datetime import datetime, timedelta
import uuid
# from intasend import APIService


views = Blueprint('views', __name__)

API_PUBLISHABLE_KEY = 'YOUR_PUBLISHABLE_KEY'

API_TOKEN = 'YOUR_API_TOKEN'

def generate_otp():
    """Generate a 6-digit OTP."""
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

#Sending OTP for signup verification
@views.route('/send_otp', methods=['GET', 'POST'])
def send_otp():
    if request.method == 'POST':
        email = request.form.get('email')

        # Generate OTP
        otp = generate_otp()

        # Store OTP with timestamp and email in session
        session['otp'] = {
            'code': otp,
            'created_at': datetime.now().isoformat(),
            'email': email  # Store email here
        }
        session.permanent = True  # Use the app's permanent session lifetime

        # Prepare email
        msg = Message('Your OTP for Verification',
                      recipients=[email],
                      body=f'Your OTP is: {otp}\nThis OTP will expire in 10 minutes.')

        try:
            mail.send(msg)
            flash('OTP sent successfully! Check your email.', 'success')
            return redirect(url_for('views.verify_otp'))
        except Exception as e:
            flash(f'Error sending OTP: {str(e)}', 'error')
    
    return render_template('send_otp.html')

#Verify OTP for signup
@views.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    """
    Route to verify OTP and redirect to sign-up.
    
    Steps:
    1. Validate OTP existence and expiration
    2. Check user-submitted OTP
    3. If verified, redirect to sign_up route
    """
    if 'otp' not in session:
        flash('Please request an OTP first', 'error')
        return redirect(url_for('views.send_otp'))

    # Get stored OTP data from session
    stored_otp = session.get('otp')

    # Ensure 'email' key exists in stored OTP
    if 'email' not in stored_otp:
        flash('Email not found in OTP data. Please request a new OTP.', 'error')
        session.pop('otp', None)  # Clear OTP from session
        return redirect(url_for('views.send_otp'))

    otp_created_at = datetime.fromisoformat(stored_otp['created_at'])

    # Validate OTP age
    if datetime.now() - otp_created_at > timedelta(minutes=10):
        session.pop('otp', None)
        flash('OTP has expired. Please request a new one.', 'error')
        return redirect(url_for('views.send_otp'))

    if request.method == 'POST':
        user_otp = request.form.get('otp')

        if user_otp == stored_otp['code']:
            # Store email in session for sign-up route to access
            session['verified_email'] = stored_otp['email']

            # Clear the OTP from session after successful verification
            session.pop('otp', None)

            # Redirect to sign_up route
            return redirect(url_for('auth.sign_up'))
        else:
            flash('Invalid OTP. Please try again.', 'error')

    return render_template('verify_otp.html')

#Rendering the home page
@views.route('/')
def home():

    items = Product.query.filter_by(flash_sale=True)

    return render_template('home.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])

#Adding products to the cart
@views.route('/add-to-cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    item_to_add = Product.query.get(item_id)
    item_exists = Cart.query.filter_by(product_link=item_id, customer_link=current_user.id).first()
    if item_exists:
        try:
            item_exists.quantity = item_exists.quantity + 1
            db.session.commit()
            flash(f' Quantity of { item_exists.product.product_name } has been updated')
            return redirect(request.referrer)
        except Exception as e:
            print('Quantity not Updated', e)
            flash(f'Quantity of { item_exists.product.product_name } not updated')
            return redirect(request.referrer)

    new_cart_item = Cart()
    new_cart_item.quantity = 1
    new_cart_item.product_link = item_to_add.id
    new_cart_item.customer_link = current_user.id

    try:
        db.session.add(new_cart_item)
        db.session.commit()
        flash(f'{new_cart_item.product.product_name} added to cart')
    except Exception as e:
        print('Item not added to cart', e)
        flash(f'{new_cart_item.product.product_name} has not been added to cart')

    return redirect(request.referrer)

#Viewing Cart Contents
@views.route('/cart')
@login_required
def show_cart():
    customer = Customer.query.get(current_user.id)
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    amount = 0
    for item in cart:
        amount += item.product.current_price * item.quantity

    return render_template('cart.html', cart=cart, amount=amount, total=amount+200, customer = customer)


#Adding product to cart
@views.route('/pluscart')
@login_required
def plus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        cart_item.quantity = cart_item.quantity + 1
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)
    
#reducing product to cart
@views.route('/minuscart')
@login_required
def minus_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        
        # Ensure quantity does not go below 1
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)

#removing cart items
@views.route('removecart')
@login_required
def remove_cart():
    if request.method == 'GET':
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        db.session.delete(cart_item)
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()

        amount = 0

        for item in cart:
            amount += item.product.current_price * item.quantity

        data = {
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        }

        return jsonify(data)

# Placing an Order
@views.route('/place-order', methods=['POST'])
@login_required
def place_order():
    # Retrieve the current customer based on the logged-in user
    customer = Customer.query.get(current_user.id)  # Adjust according to your user model

    if not customer or not customer.address:
        flash('You must provide an address to complete the purchase.', 'warning')
        customer_cart = Cart.query.filter_by(customer_link=current_user.id).all()  # Get customer's cart items
        return render_template('cart.html', cart=customer_cart, customer=customer)  # Pass customer to the template

    selected_items = request.form.getlist('selected_items')
    if not selected_items:
        flash('No items selected.', 'warning')
        customer_cart = Cart.query.filter_by(customer_link=current_user.id).all()
        return render_template('cart.html', cart=customer_cart, customer=customer)

    customer_cart = Cart.query.filter(Cart.id.in_(selected_items)).all()

    if customer_cart:
        try:
            total = 0
            order_details = ""
            for item in customer_cart:
                if item.product.in_stock == 0:
                    flash(f'The product {item.product.product_name} is out of stock.', 'danger')
                    return render_template('cart.html', cart=customer_cart, customer=customer)  # Pass customer to the template
                total += item.product.current_price * item.quantity
                order_details += f'Product: {item.product.product_name}\nQuantity: {item.quantity}\n\n'

            # Simulate a payment process (replace this with your actual payment logic if needed)
            payment_successful = True  # Simulating payment success, change as needed

            if payment_successful:
                payment_id = str(uuid.uuid4())  # Generate a unique payment ID

                for item in customer_cart:
                    new_order = Order()
                    new_order.quantity = item.quantity
                    new_order.price = item.product.current_price
                    new_order.status = 'Pending'  # Update to your actual payment status
                    new_order.payment_id = payment_id  # Use the generated payment ID

                    new_order.product_link = item.product_link
                    new_order.customer_link = item.customer_link

                    db.session.add(new_order)

                    # Update product stock
                    product = Product.query.get(item.product_link)
                    product.in_stock -= item.quantity

                    # Delete the cart item after creating the order
                    db.session.delete(item)

                db.session.commit()

                # Send order confirmation email
                msg = Message('Order Confirmation', recipients=[customer.email])
                msg.body = (
                    'Dear Customer,\n\n'
                    '**ORDER CONFIRMATION**\n\n'
                    f'{order_details}'
                    f'Total Amount: PHP{total:.2f}\n\n'
                    'Payment Method: Cash On Delivery\n\n'
                    'Courier: LBC\n\n'
                    'Thank you for your order. Please wait for the courier to deliver your package.\n\n'
                    'Best regards,\n'
                    'Findify'
                )
                mail.send(msg)

                flash('Order Placed Successfully', 'success')
                return redirect('/orders')
            else:
                flash('Payment failed. Please try again.', 'danger')
                return render_template('cart.html', cart=customer_cart, customer=customer)  # Pass customer to the template

        except Exception as e:
            print(e)
            flash('Order not placed due to an error.', 'danger')
            db.session.rollback()  # Roll back the session if there is an error
            return render_template('cart.html', cart=customer_cart, customer=customer)  # Pass customer to the template
    else:
        flash('Your cart is empty.', 'warning')
        return render_template('cart.html', cart=customer_cart, customer=customer)

#Buying a product directly
@views.route('/buy-now/<int:product_id>', methods=['GET', 'POST'])
@login_required
def buy_now(product_id):
    # Retrieve the current customer based on the logged-in user
    customer = Customer.query.get(current_user.id)  # Adjust according to your user model
    if not customer or not customer.address:
        flash('You must provide an address to complete the purchase.', 'warning')
        return redirect(url_for('views.view', product_id=product_id))  # Redirect to product detail page
    
    product = Product.query.get(product_id)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('views.home'))  # Redirect to home page
    
    # Get quantity from query parameter, default to 1 if not provided
    quantity = int(request.args.get('quantity', 1))
    
    if product.in_stock < quantity:
        flash(f'Only {product.in_stock} items available for {product.product_name}.', 'danger')
        return redirect(url_for('views.view', product_id=product_id))  # Redirect to product detail page
    
    try:
        # Simulate a payment process (replace this with your actual payment logic if needed)
        payment_successful = True  # Simulating payment success, change as needed
        if payment_successful:
            new_order = Order()
            new_order.quantity = quantity
            new_order.price = product.current_price * quantity
            new_order.status = 'Pending'  # Update to your actual payment status
            new_order.payment_id = 'SimulatedPaymentID'  # Simulated payment ID
            new_order.product_link = product_id
            new_order.customer_link = customer.id
            db.session.add(new_order)
            
            # Update product stock
            product.in_stock -= quantity
            db.session.commit()
            
            # Send order confirmation email
            msg = Message('Order Confirmation', recipients=[customer.email])
            msg.body = (
                'Dear Customer,\n\n'
                '**ORDER CONFIRMATION**\n\n'
                f'Product: {product.product_name}\n'
                f'Quantity: {new_order.quantity}\n'
                f'Total Amount: PHP{new_order.price:.2f}\n\n'
                'Payment Method: Cash On Delivery\n\n'
                'Courier: LBC\n\n'
                'Thank you for your order. Please wait for the courier to deliver your package.\n\n'
                'Best regards,\n'
                'Findify'
            )
            mail.send(msg)
            flash('Order Placed Successfully', 'success')
            return redirect('/orders')
        else:
            flash('Payment failed. Please try again.', 'danger')
            return redirect(url_for('views.view', product_id=product_id))  # Redirect to product detail page
    except Exception as e:
        print(e)
        flash('Order not placed due to an error.', 'danger')
        db.session.rollback()  # Roll back the session if there is an error
        return redirect(url_for('views.view', product_id=product_id))

#Viewing Customer Orders
@views.route('/orders')
@login_required
def order():
    orders = Order.query.filter_by(customer_link=current_user.id).all()
    return render_template('orders.html', orders=orders)

#Searching Products by Category, Name, Price, and Rating
@views.route('/search', methods=['GET', 'POST'])
def search():
    items = []
    # Handle POST request with search filters
    if request.method == 'POST':
        category = request.form.get('category')
        search_query = request.form.get('search')
        min_price = request.form.get('min_price', type=float)
        max_price = request.form.get('max_price', type=float)
        min_rating = request.form.get('min_rating', type=int)  # Add this to filter by rating
        popularity = request.form.get('popularity')  # Get the popularity filter

        # Apply filters based on provided criteria
        query = db.session.query(Product, func.avg(Review.rating).label('average_rating')) \
            .outerjoin(Review, Product.id == Review.product_id) \
            .group_by(Product.id)
        
        # Apply filters
        if category:
            query = query.filter(Product.category == category)
        if search_query:
            query = query.filter(Product.product_name.ilike(f'%{search_query}%'))
        if min_price is not None:
            query = query.filter(Product.current_price >= min_price)
        if max_price is not None:
            query = query.filter(Product.current_price <= max_price)
        if min_rating is not None:  # Add this condition to filter by rating
            query = query.having(func.avg(Review.rating) >= min_rating)
        
        # Apply popularity filter
        if popularity == 'most':
            query = query.join(Order, Product.id == Order.product_link) \
                         .group_by(Product.id) \
                         .order_by(func.sum(Order.quantity).desc())
        elif popularity == 'least':
            query = query.join(Order, Product.id == Order.product_link) \
                         .group_by(Product.id) \
                         .order_by(func.sum(Order.quantity).asc())

        items = query.all()

        return render_template(
            'search.html',
            items=items,
            cart=Cart.query.filter_by(customer_link=current_user.id).all() if current_user.is_authenticated else []
        )

    # Handle GET request with search query (for initial page load)
    search_query = request.args.get('search')
    if search_query:
        items = Product.query.filter(Product.product_name.ilike(f'%{search_query}%')).all()
        return render_template(
            'view.html',
            items=items,
            cart=Cart.query.filter_by(customer_link=current_user.id).all() if current_user.is_authenticated else []
        )

    # Handle the case when no form was submitted (GET request with no query)
    return render_template('search.html')


#Viewing a Product with detail, reviews, and add to wishlist
@views.route('/view', methods=['GET'])
def view():
    product_id = request.args.get('product_id')
    
    if product_id:
        # Fetch the specific product
        item = Product.query.get(product_id)
        
        if item:
            # Fetch reviews for this specific product
            reviews = Review.query.filter_by(product_id=product_id).all()
            
            # Prepare item data
            item_data = {
                'id': item.id,
                'product_name': item.product_name,
                'product_picture': item.product_picture,
                'current_price': item.current_price,
                'previous_price': item.previous_price,
                'description': item.description,
                'in_stock': item.in_stock
            }
            
            return render_template(
                'view.html', 
                items=[item_data],  # Wrap in list to match existing template
                reviews=reviews,
                cart=Cart.query.filter_by(customer_link=current_user.id).all() if current_user.is_authenticated else []
            )
    
    # If no product ID is provided, show an error or redirect
    flash('No product selected', 'error')
    return redirect(url_for('views.index'))

#Adding Product to Wishlist
@views.route('/add-to-wishlist/<int:item_id>')
@login_required
def add_to_wishlist(item_id):
    # Get the product from the Product table
    item_to_add = Product.query.get(item_id)  
    if not item_to_add:
        flash('Product not found')
        return redirect(request.referrer)

    # Check if the product is already in the wishlist for the current user
    item_exists = Wishlist.query.filter_by(product_link=item_id, customer_link=current_user.id).first()
    if item_exists:
        flash(f'{item_to_add.product_name} is already in your wishlist')
        return redirect(request.referrer)

    # Create a new Wishlist entry
    new_wishlist_item = Wishlist()
    new_wishlist_item.product_link = item_to_add.id
    new_wishlist_item.customer_link = current_user.id

    try:
        db.session.add(new_wishlist_item)
        db.session.commit()
        flash(f'{item_to_add.product_name} added to your wishlist')  # Use item_to_add to access product details
    except Exception as e:
        print(f'Item not added to wishlist: {e}')
        flash(f'{item_to_add.product_name} has not been added to your wishlist')

    return redirect(request.referrer)

#Displaying Customer Wishilist
@views.route('/wishlist')
@login_required
def show_wishlist():
    # Fetch all wishlist items for the current user
    wishlist = Wishlist.query.filter_by(customer_link=current_user.id).all()

    return render_template('wishlist.html', wishlist=wishlist)

#Removing Product from Wishlist
@views.route('remove-wishlist')
@login_required
def remove_wishlist():
    if request.method == 'GET':
        wishlist_id = request.args.get('wishlist_id')  # Get the wishlist ID from the request
        wishlist_item = Wishlist.query.get(wishlist_id)  # Query the wishlist item
        
        if wishlist_item:  # Check if the wishlist item exists
            db.session.delete(wishlist_item)  # Delete the wishlist item
            db.session.commit()  # Commit the changes to the database

        # Fetch the updated wishlist for the current user (if needed)
        wishlist = Wishlist.query.filter_by(customer_link=current_user.id).all()

        # Prepare a response (optional)
        data = {
            'message': 'Item removed from wishlist successfully.',
            'remaining_items': len(wishlist)  # Total items left in the wishlist
        }

        return jsonify(data)
 
#Searching Products (Once image is clicked) by Category, Name, Price, and Rating
@views.route('/goto', methods=['GET', 'POST'])
@login_required  # Ensure the user is logged in
def goto():
    if request.method == 'POST':
        search_query = request.form.get('search')
        
        # Fetch wishlist items for the current user
        wishlist_items = Wishlist.query.filter_by(customer_link=current_user.id).all()
        
        # Filter products in the wishlist based on the search query
        filtered_items = [
            item for item in wishlist_items if search_query.lower() in item.product.product_name.lower()
        ]

        return render_template('wishlist.html', wishlist=filtered_items,  # Pass filtered wishlist to template
                               cart=Cart.query.filter_by(customer_link=current_user.id).all())

    return redirect(url_for('views.wishlist'))  # Redirect to wishlist page if GET request

#Viewing Product Reviews
@views.route('/product/<int:product_id>', methods=['GET'])
def product_review(product_id):
    # Retrieve the specific product
    product = Product.query.get_or_404(product_id)
    # Fetch reviews related to the product
    reviews = Review.query.filter_by(product_id=product.id).all()

    search_query = request.args.get('search')
    if search_query:
        # Fetch products that match the search query
        items = Product.query.filter(Product.product_name.ilike(f'%{search_query}%')).all()
        return render_template(
            'product_reviews.html',
            items=items,
            product=product,
            reviews=reviews,
            cart=Cart.query.filter_by(customer_link=current_user.id).all() if current_user.is_authenticated else []
        )

    return render_template(
        'product_reviews.html',
        product=product,
        reviews=reviews,
        cart=Cart.query.filter_by(customer_link=current_user.id).all() if current_user.is_authenticated else []
    )

#Viewing Company Information of the Founders
@views.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        if not name or not email or not subject or not message:
            flash('All fields are required!', category='error')
        else:
            try:
                # Create the email content
                msg = Message(
                    subject=f"Contact Form Submission: {subject}",
                    sender=email,
                    recipients=[os.getenv('EMAIL_USER', 'afindify@gmail.com')]
                )
                msg.body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

                # Send the email
                mail.send(msg)

                flash('Your message has been sent!', category='success')
            except Exception as e:
                flash(f'An error occurred while sending your message: {str(e)}', category='error')

    return render_template('contact.html')

#Customer Send Contacts
@views.route('/contact-us', methods=['GET'])
def contact_us():
    return render_template('contact_us.html')

#Viewing Company FAQs
@views.route('/faqs', methods=['GET'])
def faqs():
    return render_template('faqs.html')
