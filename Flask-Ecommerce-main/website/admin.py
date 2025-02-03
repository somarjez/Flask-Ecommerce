from flask import Blueprint, render_template, flash, send_from_directory, redirect, url_for, request
from flask_login import login_required, current_user
from .forms import ShopItemsForm, OrderForm, CustomerUpdateForm, CustomerReviewForm, ProfileUpdate, SellerRequestForm
from werkzeug.utils import secure_filename
from .models import Product, Order, Customer, Review
from . import db
import os
from flask import flash, redirect, render_template, url_for
from werkzeug.utils import secure_filename
from flask import current_app
import os
from flask import render_template, redirect, flash, current_app, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from flask import Flask, redirect, url_for, session, request
from flask_sqlalchemy import SQLAlchemy
import requests
from oauthlib.oauth2 import WebApplicationClient

admin = Blueprint('admin', __name__)

#File directory
@admin.route('/media/<path:filename>')
def get_image(filename):
    return send_from_directory('../media', filename)

#Adding Shop Items
@admin.route('/add-shop-items', methods=['GET', 'POST'])
@login_required
def add_shop_items():
    # Check if the current user is authorized to add shop items (admin or verified user)
    if current_user.id == 1 or (current_user.is_verified and current_user.id == current_user.id):
        form = ShopItemsForm()  # Initialize the form for adding shop items

        if form.validate_on_submit():
            # Extract data from the form
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data
            description = form.description.data
            category = form.category.data   # Get the product description
            file = form.product_picture.data  # Get the uploaded product picture

            # Set the media directory path to the project root
            media_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'media'))

            # Check if the media directory exists; if not, create it
            if not os.path.exists(media_dir):
                os.makedirs(media_dir)

            if file:
                # Secure the filename and save the uploaded file
                file_name = secure_filename(file.filename)
                file_path = os.path.join(media_dir, file_name)  # Full path for saving
                file.save(file_path)

                # Store the relative file path for database storage
                relative_file_path = os.path.join('media', file_name)
            else:
                relative_file_path = None  # Handle cases where no file is uploaded

            # Create a new product instance and assign the current user as the seller
            new_shop_item = Product(
                product_name=product_name,
                current_price=current_price,
                previous_price=previous_price,
                in_stock=in_stock,
                flash_sale=flash_sale,
                description=description,  # Store the product description
                category=category, 
                product_picture=relative_file_path,  # Use the relative file path for storage
                customer_id=current_user.id  # Assign current user's ID as seller
            )

            try:
                db.session.add(new_shop_item)  # Add the new product to the session
                db.session.commit()  # Commit the changes to the database
                flash(f'{product_name} added successfully', 'success')  # Flash success message
                return redirect(url_for('admin.add_shop_items'))  # Redirect to the same page to avoid form resubmission
            except Exception as e:
                db.session.rollback()  # Rollback the session in case of an error
                print(e)
                flash('Product not added! Please try again.', 'error')  # Flash error message

        # Render the form for adding shop items
        return render_template('add_shop_items.html', form=form)

    # If the user is not authorized, render a 404 page
    return render_template('404.html')


# Viewing Shop Items
@admin.route('/shop-items', methods=['GET', 'POST'])
@login_required
def shop_items():
    # Only allow verified users or the super admin (id == 1) to view shop items
    if current_user.is_verified or current_user.id == 1:
        # Get the page number from the query string (default to 1 if not provided)
        page = request.args.get('page', 1, type=int)

        # Set the number of products per page to 5
        items_per_page = 5

        # If the user is a super admin, retrieve all products; otherwise, filter by customer_id
        if current_user.id == 1:
            items = Product.query.order_by(Product.date_added).paginate(page=page, per_page=items_per_page, error_out=False)
            return render_template('super_shopitems.html', items=items.items, pagination=items)
        else:
            items = Product.query.filter_by(customer_id=current_user.id).order_by(Product.date_added).paginate(page=page, per_page=items_per_page, error_out=False)
            return render_template('shop_items.html', items=items.items, pagination=items)

    # If user is not verified or admin, return 404
    return render_template('404.html')

#Adding Products to Archive Section
@admin.route('/archive-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def archive_item(item_id):
    if current_user.is_verified == 1 or current_user.id == 1:
        try:
            # Check if the item exists and belongs to the current user (check both customer_id and seller_id)
            item_to_archive = Product.query.filter(
                (Product.id == item_id) & 
                ((Product.seller_id == current_user.id) | (Product.customer_id == current_user.id))
            ).first()

            if not item_to_archive:
                flash('You do not have permission to archive this item or the item does not exist.')
                return redirect('/shop-items')

            # Archive the item (set archived flag to 1)
            item_to_archive.archived = 1
            db.session.commit()
            flash('Item archived successfully')
            return redirect('/shop-items')
        except Exception as e:
            print(f"Error archiving item: {e}")
            flash('Error archiving item!')
            return redirect('/shop-items')
    return render_template('404.html')

#Removing Products in the Archived Section
@admin.route('/unarchive-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def unarchive_item(item_id):
    if current_user.is_verified == 1 or current_user.id == 1:
        try:
            # Check if the item exists and belongs to the current user (check both customer_id and seller_id)
            item_to_unarchive = Product.query.filter(
                (Product.id == item_id) & 
                ((Product.seller_id == current_user.id) | (Product.customer_id == current_user.id))
            ).first()

            if not item_to_unarchive:
                flash('You do not have permission to unarchive this item or the item does not exist.')
                return redirect('/archived-items')

            # Unarchive the item (set archived flag to 0)
            item_to_unarchive.archived = 0
            db.session.commit()
            flash('Item unarchived successfully')
            return redirect('/archived-items')
        except Exception as e:
            print(f"Error unarchiving item: {e}")
            flash('Error unarchiving item.')
            return redirect('/archived-items')

    return render_template('404.html')

#Displaying/Showing Archived Items
@admin.route('/archived-items', methods=['GET'])
@login_required
def archived_items():
    if current_user.is_verified == 1 or current_user.id == 1:
        try:
            # Get the page number from the URL, default to 1 if not provided
            page = request.args.get('page', 1, type=int)
            
            # Fetch archived items for the current user, paginated by 5 per page
            archived_items = Product.query.filter(
                (Product.archived == 1) & 
                ((Product.seller_id == current_user.id) | (Product.customer_id == current_user.id))
            ).paginate(page=page, per_page=5, error_out=False)

            return render_template('archived_items.html', items=archived_items.items, pagination=archived_items)

        except Exception as e:
            print(f"Error fetching archived items: {e}")
            flash('Error fetching archived items.')
            return redirect('/shop-items')

    return render_template('404.html')

#Restoring Archived Items
@admin.route('/restore-item/<int:item_id>', methods=['GET'])
@login_required
def restore_item(item_id):
    if current_user.is_verified == 1 or current_user.id == 1:
        try:
            # Find the product by ID
            product = Product.query.get_or_404(item_id)
            
            # Check if the current user is the owner of the product
            if product.seller_id == current_user.id or product.customer_id == current_user.id:
                product.archived = 0  # Restore the item (set archived = 0)
                db.session.commit()
                flash('Product restored successfully.')
            else:
                flash('You do not have permission to restore this product.')
            
            return redirect('/archived-items')
        except Exception as e:
            print(f"Error restoring item: {e}")
            flash('Error restoring item.')
            return redirect('/archived-items')
    return render_template('404.html')

#Deleting Items or Products
@admin.route('/delete-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def delete_item(item_id):
    if current_user.is_verified == 1 or current_user.id == 1:
        try:
            # Super admin can delete any item, while regular users can delete only their own items
            if current_user.id == 1:
                # If super admin, fetch the item without filtering by customer_id
                item_to_delete = Product.query.filter_by(id=item_id).first()
            else:
                # If not super admin, fetch the item and ensure it belongs to the current user
                item_to_delete = Product.query.filter_by(id=item_id, customer_id=current_user.id).first()

            if not item_to_delete:
                flash('You do not have permission to delete this item.')
                return render_template('404.html')

            # Delete the item
            db.session.delete(item_to_delete)
            db.session.commit()
            flash('One item deleted successfully')
            return redirect('/shop-items')
        except Exception as e:
            print('Item not deleted', e)
            flash('Item not deleted!!')
            return redirect('/shop-items')

    return render_template('404.html')

#Updating Items/Products
@admin.route('/update-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    if current_user.is_verified == 1 or current_user.id == 1:
        # Fetch the item to update
        item_to_update = Product.query.filter_by(id=item_id).first()

        if not item_to_update:
            flash('Item not found.')
            return render_template('404.html')

        form = ShopItemsForm()

        if request.method == 'GET':
            # Pre-fill form with existing item data only on GET request
            form.product_name.data = item_to_update.product_name
            form.current_price.data = item_to_update.current_price
            form.previous_price.data = item_to_update.previous_price
            form.in_stock.data = item_to_update.in_stock
            form.description.data = item_to_update.description
            form.category.data = item_to_update.category
            form.flash_sale.data = item_to_update.flash_sale

        if form.validate_on_submit():
            # Update the item with the form data
            item_to_update.product_name = form.product_name.data
            item_to_update.current_price = form.current_price.data
            item_to_update.previous_price = form.previous_price.data
            item_to_update.in_stock = form.in_stock.data
            item_to_update.description = form.description.data
            item_to_update.category = form.category.data
            item_to_update.flash_sale = form.flash_sale.data

            # Handle product picture file
            file = form.product_picture.data
            if file:
                file_name = secure_filename(file.filename)

                # Set the media directory path to the project root
                media_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'media'))

                # Check if the media directory exists, if not, create it
                if not os.path.exists(media_dir):
                    os.makedirs(media_dir)

                # Save the uploaded file in the media directory
                file_path = os.path.join(media_dir, file_name)  # Full path for saving
                file.save(file_path)

                # Update the product with the new picture path
                item_to_update.product_picture = os.path.join('media', file_name)  # Relative path for the database

            try:
                db.session.commit()
                flash(f'{form.product_name.data} updated successfully')
                return redirect('/shop-items')
            except Exception as e:
                db.session.rollback()
                flash('Item Not Updated!!!')
                print('Error updating item:', e)

        return render_template('update_item.html', form=form, item=item_to_update)

    return render_template('404.html')


#Viewing Orders of Customers
@admin.route('/view-orders', methods=['GET', 'POST'])
@login_required
def order_view():
    status = request.args.get('status')  # Get the status from the URL parameters
    page = request.args.get('page', 1, type=int)  # Get the page number from the URL (default to 1)

    # Admin: Fetch all orders, filtered by status if present
    if current_user.id == 1:
        if status:
            orders = Order.query.filter_by(status=status).paginate(page=page, per_page=5, error_out=False)
        else:
            orders = Order.query.paginate(page=page, per_page=5, error_out=False)
    else:
        # Fetch only orders related to the current user's products, filtered by status if present
        query = db.session.query(Product.id).filter_by(customer_id=current_user.id)
        if status:
            orders = Order.query.filter(Order.product_link.in_(query), Order.status == status).paginate(page=page, per_page=5, error_out=False)
        else:
            orders = Order.query.filter(Order.product_link.in_(query)).paginate(page=page, per_page=5, error_out=False)

    return render_template('view_orders.html', orders=orders.items, pagination=orders)

#Updating Orders of Customers
@admin.route('/update-order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def update_order(order_id):
    form = OrderForm()

    # Fetch the order by ID
    order = Order.query.filter_by(id=order_id).first_or_404()

    # Allow admin to update any order
    if current_user.id == 1:
        if form.validate_on_submit():
            # Update the order status
            order.status = form.order_status.data
            try:
                db.session.commit()
                flash(f'Order {order_id} updated successfully')
                return redirect('/view-orders')
            except Exception as e:
                print(e)
                flash(f'Order {order_id} not updated')
                return redirect('/view-orders')

        # Populate the form with the current order data
        form.order_status.data = order.status
        return render_template('order_update.html', form=form)

    # Allow sellers to update orders for products they uploaded
    seller_product_ids = db.session.query(Product.id).filter_by(customer_id=current_user.id).all()
    seller_product_ids = [p.id for p in seller_product_ids]  # Convert result to a list of IDs

    if order.customer_link == current_user.id or order.product_link in seller_product_ids:
        if form.validate_on_submit():
            # Update the order status
            order.status = form.order_status.data
            try:
                db.session.commit()
                flash(f'Order {order_id} updated successfully')
                return redirect('/view-orders')
            except Exception as e:
                print(e)
                flash(f'Order {order_id} not updated')
                return redirect('/view-orders')

        # Populate the form with the current order data
        form.order_status.data = order.status
        return render_template('order_update.html', form=form)

    # If the user is not authorized, show an error
    flash('You do not have permission to update this order.')
    return render_template('404.html')

#Displaying Customers
@admin.route('/customers', methods=['GET'])
@login_required
def display_customers():
    if current_user.is_verified == 1 or current_user.id == 1:  # Check if user is verified or admin
        # Get the page number from the query string (default to 1 if not provided)
        page = request.args.get('page', 1, type=int)
        
        # Set the number of customers per page to 7
        customers_per_page = 7
        
        # Query the database to get paginated customers
        customers = Customer.query.paginate(page=page, per_page=customers_per_page, error_out=False)
        
        # If the current user is a regular user
        if current_user.id != 1:
            return render_template('customers.html', customers=customers.items, pagination=customers)
        
        # Admin access: render admin customer view
        return render_template('admin_customer.html', customers=customers.items, pagination=customers)
    
    return render_template('404.html')

#Seller Dashboard Display
@admin.route('/admin-page')
@login_required
def admin_page():
      # Get the product IDs owned by the current user
    user_product_ids = db.session.query(Product.id).filter_by(customer_id=current_user.id)

    # Fetch the relevant orders along with the order date
    sales_data = db.session.query(
        Product.product_name,
        db.func.sum(Order.quantity).label('total_sold'),
        db.func.sum(Order.price).label('total_revenue'),
        Order.order_date  # Include the order date
    ).join(Order, Order.product_link == Product.id) \
     .filter(Order.product_link.in_(user_product_ids)) \
     .group_by(Product.id, Order.order_date)  # Group by order_date to ensure proper aggregation
     
    sales_data = sales_data.all()

    return render_template('admin.html', sales_data=sales_data)

#Super Admin Dashboard Display
@admin.route('/superadmin-page')
@login_required
def superadmin_page():
    if current_user.id == 1:
        return render_template('super_admin.html')
    return render_template('404.html')

#Updating Customer Information
@admin.route('/update-customer/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def update_customer(customer_id):
    # Check if the current user has permission to update the customer
    if current_user.id == 1:
        # Fetch the customer to update
        customer_to_update =Customer.query.get(customer_id)  # Ensure this is the correct model

        if not customer_to_update:
            flash('Customer not found.', 'error')
            return render_template('404.html')

        form = CustomerUpdateForm(obj=customer_to_update)  # Pre-fill form with existing customer data

        if form.validate_on_submit():
            # Gather form data
            customer_to_update.username = form.username.data
            customer_to_update.email = form.email.data
            # customer_to_update.seller_id = form.seller_id.data or None
            customer_to_update.is_verified = form.is_verified.data  # Update the is_verified field


            try:
                db.session.commit()
                flash('Customer updated successfully', 'success')
                return redirect(url_for('admin.display_customers'))  # Redirect to the customers list
            except Exception as e:
                print('Customer not updated', e)
                flash('Failed to update customer!', 'error')

        # Render the template with the form and customer data
        return render_template('update_customer.html', form=form, customer=customer_to_update)

    return render_template('404.html')

#Deleting Customer Information
@admin.route('/delete-customer/<int:customer_id>', methods=['GET','POST'])
@login_required
def delete_customer(customer_id):
    # Check if the current user has permission to delete the customer
    if current_user.id == 1:
        # Fetch the customer to delete
        customer_to_delete = Customer.query.get(customer_id)  # Ensure this is the correct model

        if not customer_to_delete:
            flash('Customer not found.', 'error')
            return render_template('404.html')

        try:
            db.session.delete(customer_to_delete)  # Delete the customer
            db.session.commit()  # Commit the changes
            flash('Customer deleted successfully', 'success')
        except Exception as e:
            print('Customer not deleted', e)
            flash('Failed to delete customer!', 'error')

        return redirect(url_for('admin.display_customers'))  # Redirect to the customers list

    return render_template('404.html')

#Submitting Reviews
@admin.route('/submit-review/<int:product_id>', methods=['GET', 'POST'])
@login_required
def submit_review(product_id):
    product = Product.query.get_or_404(product_id)  # Fetch the product or return 404
    form = CustomerReviewForm()  # Initialize the review form

    if form.validate_on_submit():
        # Check if the review already exists for the current user and product
        existing_review = Review.query.filter_by(customer_id=current_user.id, product_id=product.id).first()
        if existing_review:
            flash('You have already submitted a review for this product.', 'warning')
            return redirect(url_for('views.order'))   # Render current user's orders page

        try:
            # Save the review data to the database
            review = Review(
                customer_id=current_user.id,  # Use current_user.id for customer_id
                product_id=product.id,         # Use product_id from the URL
                review_text=form.review_text.data,
                rating=form.rating.data
            )
            db.session.add(review)
            db.session.commit()  # Commit the new review to the database
            flash('Review submitted successfully!', 'success')
            return redirect(url_for('views.order'))   # Render current user's orders page
        except Exception as e:
            db.session.rollback()  # Rollback if there was an error
            flash('Error submitting review. Please try again.', 'danger')
            print(f'Review not saved: {e}')  # Debug output for the error

    # Render the form when GET request or validation fails
    return render_template('submit_review.html', form=form, product=product)

# #Viewing Basic Sales Reports
# @admin.route('/reports/basic-sales')
# @login_required
# def basic_sales_reports():
#     # Get the product IDs owned by the current user
#     user_product_ids = db.session.query(Product.id).filter_by(customer_id=current_user.id)

#     # Fetch the relevant orders along with the order date
#     sales_data = db.session.query(
#         Product.product_name,
#         db.func.sum(Order.quantity).label('total_sold'),
#         db.func.sum(Order.price).label('total_revenue'),
#         Order.order_date  # Include the order date
#     ).join(Order, Order.product_link == Product.id) \
#      .filter(Order.product_link.in_(user_product_ids)) \
#      .group_by(Product.id, Order.order_date)  # Group by order_date to ensure proper aggregation
     
#     sales_data = sales_data.all()

#     return render_template('basic_sales_report.html', sales_data=sales_data)

# Viewing Basic Sales Reports
@admin.route('/reports/basic-sales')
@login_required
def basic_sales_reports():
    # Check if the current user is the super admin
    if current_user.id == 1:
        # Fetch all relevant orders along with the order date
        sales_data = db.session.query(
            Product.product_name,
            db.func.sum(Order.quantity).label('total_sold'),
            db.func.sum(Order.price).label('total_revenue'),
            Order.order_date  # Include the order date
        ).join(Order, Order.product_link == Product.id) \
         .group_by(Product.id, Order.order_date)  # Group by order_date to ensure proper aggregation
        template = 'admin_sales.html'
    else:
        # Get the product IDs owned by the current user
        user_product_ids = db.session.query(Product.id).filter_by(customer_id=current_user.id)

        # Fetch the relevant orders along with the order date
        sales_data = db.session.query(
            Product.product_name,
            db.func.sum(Order.quantity).label('total_sold'),
            db.func.sum(Order.price).label('total_revenue'),
            Order.order_date  # Include the order date
        ).join(Order, Order.product_link == Product.id) \
         .filter(Order.product_link.in_(user_product_ids)) \
         .group_by(Product.id, Order.order_date)  # Group by order_date to ensure proper aggregation
        template = 'basic_sales_report.html'
     
    sales_data = sales_data.all()

    return render_template(template, sales_data=sales_data)

#Viewing Revenue Reports
@admin.route('/reports/revenue')
@login_required
def revenue_reports():
    # Get the product IDs owned by the current user
    user_product_ids = db.session.query(Product.id).filter_by(customer_id=current_user.id)

    # Query revenue data
    revenue_data = db.session.query(
        db.func.date(Order.order_date).label('order_date'),
        db.func.sum(Order.price).label('total_revenue')
    ).filter(Order.product_link.in_(user_product_ids)) \
    .group_by(db.func.date(Order.order_date)).all()

    # Render template and pass revenue data
    return render_template('revenue_reports.html', revenue_data=revenue_data)

#Backup File Directory
@admin.route('/media/<path:filename>')
def media_files(filename):
    # Use the absolute path to the media folder with standardized slashes
    media_dir = r'C:/Users/jramo/Downloads/ECOMMERCE_BASE/Flask-Ecommerce-main/media'
    return send_from_directory(media_dir, filename)


#Requesting Seller Verification
@admin.route('/request-seller', methods=['GET', 'POST'])
@login_required
def request_seller():
    # Check if the current user is already verified
    if current_user.is_verified == 1:
        flash('You are already a verified seller.', 'info')
        return redirect(url_for('views.home'))  # Redirect to the home page

    # Check if the current user has already submitted a request
    if current_user.is_verified == 2:  # Assuming 0 indicates a pending request
        flash('The admin is processing your request.', 'info')
        return redirect(url_for('views.home'))  # Redirect to the home page

    form = SellerRequestForm()  # Initialize the SellerRequestForm

    if form.validate_on_submit():
        # Extract data from the form
        bir_number = form.bir_number.data
        valid_id = form.valid_id.data  # Get the uploaded valid ID

        # Set the media directory path to the project root
        media_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'media'))

        # Check if the media directory exists; if not, create it
        if not os.path.exists(media_dir):
            os.makedirs(media_dir)

        if valid_id:
            # Secure the filename and save the uploaded file
            file_name = secure_filename(valid_id.filename)
            file_path = os.path.join(media_dir, file_name)  # Full path for saving
            valid_id.save(file_path)

            # Store the relative file path for database storage
            relative_file_path = os.path.join('media', file_name)
        else:
            relative_file_path = None  # Handle cases where no file is uploaded

        # Update the current user's record with the bir_number and valid_id
        current_user.bir_number = bir_number
        current_user.valid_id = relative_file_path  # Save the relative path to valid_id
        current_user.is_verified = 2  # Update the request status to 'pending'

        # Debugging: Check the values before committing
        print(f"Submitting Seller Request: BIR Number: {bir_number}, Valid ID: {relative_file_path}")
        
        # Commit the changes to the database
        try:
            db.session.commit()  
            flash('Seller request submitted successfully', 'success')  # Flash success message
            return redirect(url_for('views.home'))  # Redirect to the home page
        except Exception as e:
            db.session.rollback()  # Rollback in case of an error
            print(f"Error committing to database: {e}")  # Log the error
            flash('Error submitting seller request', 'danger')

    # Render the form for seller request
    return render_template('seller_request.html', form=form)


#SuperAdmin Management of Seller Requests
@admin.route('/manage-seller-requests', methods=['GET', 'POST'])
@login_required
def manage_seller_requests():
    # Ensure only super admin can access this route
    if current_user.id == 1:  # Assuming 1 is the super admin ID
        try:
            # Get the page number from the URL, default to 1 if not provided
            page = request.args.get('page', 1, type=int)
            
            # Fetch customers with both bir_number and valid_id present, paginated by 5 per page
            customers = Customer.query.filter(Customer.bir_number.isnot(None), Customer.valid_id.isnot(None)) \
                .paginate(page=page, per_page=5, error_out=False)

            return render_template('manage_seller_requests.html', customers=customers.items, pagination=customers)

        except Exception as e:
            print(f"Error fetching seller requests: {e}")
            flash('Error fetching seller requests.')
            return redirect('/admin-dashboard')

    # Handle unauthorized access
    return render_template('404.html')  # Or redirect to a different page

#SuperAdmin Approval of Seller Requests
@admin.route('/approve-seller/<int:customer_id>', methods=['POST'])
@login_required
def approve_seller(customer_id):
    # Ensure only the admin can approve seller requests
    if current_user.id != 1:
        return render_template('404.html')  # Render 404 if not admin

    customer = Customer.query.get(customer_id)
    if customer:
        customer.is_verified = 1  # Update verification status
        db.session.commit()  # Commit changes to the database
        flash('Seller request approved successfully!', 'success')
    else:
        flash('Customer not found.', 'danger')
    return redirect(url_for('admin.manage_seller_requests'))

#SuperAdmin Rejection of Seller Requests
@admin.route('/reject-seller/<int:customer_id>', methods=['POST'])
@login_required
def reject_seller(customer_id):
    # Ensure only the admin can reject seller requests
    if current_user.id != 1:
        return render_template('404.html')  # Render 404 if not admin

    customer = Customer.query.get(customer_id)
    if customer:
        # Instead of deleting the customer, you might want to set a status
        customer.is_verified = False  # Mark the customer as not verified or set a specific status
        customer.bir_number = None  # Optionally clear other fields related to the seller request
        customer.valid_id = None  # Clear the valid ID field

        db.session.commit()  # Commit changes to the database
        flash('Seller request rejected successfully!', 'success')
    else:
        flash('Customer not found.', 'danger')

    return redirect(url_for('admin.manage_seller_requests'))

#Customer Cancel Order
@admin.route('/cancel_order/<int:order_id>', methods=['POST'])
@login_required
def cancel_order(order_id):
    order = Order.query.get(order_id)

    # Ensure the order exists and belongs to the current user
    if order and order.customer_link == current_user.id:  # Check if the order belongs to the customer
        if order.status == 'Pending':  # Only allow cancellation for pending orders
            order.status = 'Canceled'  # Update the order status to canceled

            # Add the quantity back to the product stock
            product = Product.query.get(order.product_link)
            if product:
                product.in_stock += order.quantity

            db.session.commit()  # Commit the changes
            flash('Order has been canceled successfully!', 'success')
        else:
            flash('Order cannot be canceled because it is already ' + order.status.lower() + '.', 'danger')
    else:
        flash('Order not found or does not belong to you.', 'danger')
    return redirect(url_for('views.order', current_user=current_user.id))  # Redirect to the orders page

#Customer Delete Order
@admin.route('/delete_order/<int:order_id>', methods=['POST'])
@login_required
def delete_order(order_id):
    order = Order.query.get(order_id)

    # Ensure the order exists and belongs to the current user
    if order and order.customer_link == current_user.id:  # Check if the order belongs to the customer
        db.session.delete(order)  # Delete the order from the session
        db.session.commit()  # Commit the changes
        flash('Order has been deleted successfully!', 'success')
    else:
        flash('Order not found or does not belong to you.', 'danger')
    return redirect(url_for('views.order', current_user = current_user.id))


#Admin/Seller Update Order Status/Order Tracking
@admin.route('/admin/update_status/<int:order_id>', methods=['POST'])
@login_required
def update_status(order_id):
    order = Order.query.get(order_id)
    if order:
        if order.status == 'Completed':
            order.status = 'Delivered'
            db.session.commit()
            flash("Order status updated to 'Delivered'", "success")
        else:
            flash("Invalid operation", "danger")
    else:
        flash("Order not found", "danger")
    return redirect(url_for('views.order'))

