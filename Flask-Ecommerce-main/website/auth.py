from flask import Blueprint, render_template, flash, redirect,url_for
from .forms import LoginForm, SignUpForm, PasswordChangeForm, CustomerReviewForm, ProfileUpdate
from .models import Customer, Review
from . import db
from flask_login import login_user, login_required, logout_user, session_protected
from flask import send_from_directory, current_app, session
import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user
from flask_mail import Message
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import secrets

from . import db, mail
from .models import Customer
from .forms import ResetPasswordRequestForm, ResetPasswordForm


auth = Blueprint('auth', __name__)

#File Directoris of Profile
@auth.route('/profile/<path:filename>') 
def get_image(filename):
    return send_from_directory(os.path.join(current_app.root_path, 'profile'), filename)

#Signing Up
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    # Retrieve the verified email from session
    verified_email = session.pop('verified_email', None)
    
    form = SignUpForm()
    
    # If there's a verified email, pre-fill the email field
    if verified_email:
        form.email.data = verified_email
    
    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        password1 = form.password1.data
        password2 = form.password2.data
        
        if password1 == password2:
            new_customer = Customer()
            new_customer.email = email
            new_customer.username = username
            new_customer.password = password2
            
            try:
                db.session.add(new_customer)
                db.session.commit()
                flash('Account Created Successfully, You can now Login')
                return redirect('/login')
            except Exception as e:
                db.session.rollback()
                print(e)
                flash('Account Not Created!! Email already exists')
                
            # Clear form data
            form.email.data = ''
            form.username.data = ''
            form.password1.data = ''
            form.password2.data = ''
    
    return render_template('signup.html', form=form)

#Logging In
@auth.route('/login', methods=['GET', 'POST'])
def login():
    # Accessing the form
    form = LoginForm()
    # Checking if the form is validated
    if form.validate_on_submit():
        email = form.email.data 
        password = form.password.data
        # Checking if the email exists
        customer = Customer.query.filter_by(email=email).first()
        # Checking if the password is correct
        if customer:
            if customer.verify_password(password=password):
                login_user(customer)
                flash('You have successfully logged in.')
                # Check if the user ID is 1
                if customer.id == 1:
                    return redirect('/superadmin-page')
                else:
                    return redirect('/')
            else:
                flash('Incorrect Email or Password')
        else:
            flash('Account does not exist please Sign Up')
    # Rendering the login page
    return render_template('login.html', form=form)

#Logging Out
@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def log_out():
    #Logging out the user
    logout_user()
    flash('You have been logged out successfully.')  # Move this line above the return statement
    return redirect('/')

#Profile Page/View
@auth.route('/profile/<int:customer_id>')
@login_required
def profile(customer_id):
    # Retrieve the customer based on the ID
    customer = Customer.query.get(customer_id)
    return render_template('profile.html', customer=customer)

#Updating Customer Profile
@auth.route('/update-profile/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def update_profile(customer_id):
    customer = Customer.query.get(customer_id)

    if not customer:
        flash('Customer not found!', 'danger')
        return redirect(url_for('auth.profile')) 

    form = ProfileUpdate()

    if form.validate_on_submit():
        # Update customer details
        customer.username = form.username.data
        customer.email = form.email.data
        customer.address = form.address.data
        customer.phone_number = form.phone_number.data

        # Debugging: Check if file exists
        if form.profile_picture.data:
            picture_file = form.profile_picture.data
            picture_filename = secure_filename(picture_file.filename)
            picture_path = os.path.join(current_app.root_path, 'profile', picture_filename)
            print(f"Saving file: {picture_filename} to {picture_path}")  # Debugging line
            picture_file.save(picture_path)

            # Save filename to the database (not the full path)
            customer.profile_picture = picture_filename

        # Commit changes to the database
        db.session.commit()

        flash('Customer profile has been updated!', 'success')
        return redirect(url_for('auth.profile', customer_id=customer.id))

    # Pre-fill the form with existing customer data
    form.username.data = customer.username
    form.email.data = customer.email
    form.address.data = customer.address
    form.phone_number.data = customer.phone_number
    form.profile_picture.data = customer.profile_picture
    

    return render_template('update_profile.html', form=form, customer=customer)

#Changing Customer Password
@auth.route('/change-password/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def change_password(customer_id):
    form = PasswordChangeForm()
    customer = Customer.query.get(customer_id)
    if form.validate_on_submit():
        current_password = form.current_password.data
        new_password = form.new_password.data
        confirm_new_password = form.confirm_new_password.data

        if customer.verify_password(current_password):
            if new_password == confirm_new_password:
                customer.password = confirm_new_password
                db.session.commit()
                flash('Password Updated Successfully')
                return redirect(f'/profile/{customer.id}')
            else:
                flash('New Passwords do not match!!')

        else:
            flash('Current Password is Incorrect')

    return render_template('change_password.html', form=form, customer=customer)

#Viewing Company Terms
@auth.route('/terms')
def terms():
    return render_template('terms.html')

#Viewing Company Policy
@auth.route('/policy')
def policy():
    return render_template('policy.html')

#Viewing Company About Us
@auth.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

#Viewing Home Page
@auth.route('/home')
def home():
    return render_template('home.html')

#Customer Reset Password OTP
def send_reset_email(user):
    # Generate a unique reset token
    token = secrets.token_urlsafe(32)
    
    # Update user with new token and expiration
    user.reset_token = token
    user.reset_token_expiration = datetime.utcnow() + timedelta(hours=1)
    
    # Commit changes to the database
    db.session.commit()

    # Construct reset link
    reset_link = url_for('auth.reset_password', token=token, _external=True)

    # Create email message
    msg = Message('Password Reset Request', 
                  sender=current_app.config['MAIL_DEFAULT_SENDER'], 
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{reset_link}

If you did not make this request, simply ignore this email.

This link will expire in 1 hour.
'''
    
    # Send the email
    mail.send(msg)
@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    # Prevent logged-in users from accessing reset page
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = Customer.query.filter_by(email=form.email.data).first()
        if user:
            send_reset_email(user)
            flash('An email with password reset instructions has been sent.', 'info')
            return redirect(url_for('auth.login'))
        else:
            flash('No account found with that email address.', 'error')

    return render_template('reset_password_request.html', form=form)

#Resetting Customer Password
@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Prevent logged-in users from accessing reset page
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # Find user with the token
    user = Customer.query.filter_by(reset_token=token).first()

    # Check if token is valid and not expired
    if not user or not user.reset_token or user.reset_token_expiration < datetime.utcnow():
        flash('Invalid or expired reset token.', 'error')
        return redirect(url_for('auth.reset_password_request'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        # Hash the new password
        hashed_password = generate_password_hash(form.password.data)
        
        # Update user's password using password_hash
        user.password_hash = hashed_password
        
        # Clear the reset token
        user.reset_token = None
        user.reset_token_expiration = None
        
        # Commit changes
        db.session.commit()

        flash('Your password has been reset successfully!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', form=form)



