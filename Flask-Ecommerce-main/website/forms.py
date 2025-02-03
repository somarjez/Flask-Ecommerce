from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, PasswordField, EmailField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, length, NumberRange
from flask_wtf.file import FileField, FileRequired
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Regexp
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Email, InputRequired
from flask_wtf import FlaskForm
from wtforms import IntegerField, RadioField, SubmitField
from wtforms.validators import DataRequired, NumberRange

# Form for signing up
class SignUpForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), length(min=2)])
    password1 = PasswordField('Enter Your Password', validators=[DataRequired(), length(min=6)])
    password2 = PasswordField('Confirm Your Password', validators=[DataRequired(), length(min=6)])
    submit = SubmitField('Sign Up')

# Form for logging in
class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Enter Your Password', validators=[DataRequired()])
    submit = SubmitField('Log in')

#form for changing password
class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired(), length(min=6)])
    new_password = PasswordField('New Password', validators=[DataRequired(), length(min=6)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), length(min=6)])
    change_password = SubmitField('Change Password')

# Form for updating customer details
class CustomerUpdateForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    username = StringField('Username', validators=[DataRequired(), Length(max=100)])
    seller_id = IntegerField('Seller ID ')
    is_verified = BooleanField('Verified')

    update_customer = SubmitField('Update Customer')

# Form for updating customer profile
class ProfileUpdate(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
    username = StringField('Username', validators=[DataRequired(), Length(max=100)])
    address = StringField('Address', validators=[Length(max=200)])
    phone_number = StringField('Phone Number', validators=[Length(max=200)])
    profile_picture = FileField('Profile Picture')
    update_profile = SubmitField('Update Customer')

# Form for adding/altering products
class ShopItemsForm(FlaskForm):
    product_name = StringField('Name of Product', validators=[DataRequired()])
    current_price = FloatField('Current Price', validators=[DataRequired()])
    previous_price = FloatField('Previous Price', validators=[DataRequired()])
    in_stock = IntegerField('In Stock', validators=[DataRequired(), NumberRange(min=0)])
    product_picture = FileField('Product Picture')
    description = StringField('Description', validators=[Length(max=200)])
    category = SelectField('Category', choices=[('Living Room Furniture', 'Living Room Furniture'), ('Bedroom Furniture', 'Bedroom Furniture'),
                                                        ('Dining Room Furniture', 'Dining Room Furniture'),
                                                        ('Office Furniture', 'Office Furnitured'), ('Outdoor Furniture', 'Outdoor Furniture')])
    flash_sale = BooleanField('Flash Sale')

    add_product = SubmitField('Add Product')
    update_product = SubmitField('Update')

#Form for filtering archived and active products
class Prd(FlaskForm):
    prd = SelectField('Category', choices=[('Archived', 'Archived'), ('Active', 'Active')])

# Form for updating order tracking details
class OrderForm(FlaskForm):
    order_status = SelectField('Order Status', choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'),
                                                        ('Out for delivery', 'Out for delivery'),
                                                        ('Completed', 'Completed'), ('Canceled', 'Canceled')])

    update = SubmitField('Update Status')

#forms for customer reviews
class CustomerReviewForm(FlaskForm):
    review_text = TextAreaField('Your Review', validators=[DataRequired()])
    rating = IntegerField('Rating (1-5)', validators=[DataRequired()])
    submit_review = SubmitField('Submit Review')

    def validate_rating(form, field):
        if field.data < 1 or field.data > 5:
            raise ValidationError('Rating must be between 1 and 5.')
        
#form for seller registration
class SellerRequestForm(FlaskForm):
    bir_number = IntegerField('BIR Number', validators=[DataRequired()])
    valid_id = FileField('Valid ID (Image Link)', validators=[DataRequired()])
    
    submit_request = SubmitField('Submit Request')

#getting email verification
class EmailForm(FlaskForm):
    email = StringField('Email', 
                       validators=[DataRequired(message="Email is required"),
                                 Email(message="Please enter a valid email address")])
    submit = SubmitField('Send OTP')

#form for OTP verification
class OTPForm(FlaskForm):
    otp = StringField('OTP Code',
                     validators=[DataRequired(message="OTP is required"),
                               Length(min=6, max=6, message="OTP must be 6 digits"),
                               Regexp(r'^\d{6}$', message="OTP must contain only digits")])
    submit = SubmitField('Verify OTP')

#form for requesting password reset
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', 
                       validators=[DataRequired(message="Email is required"),
                                 Email(message="Please enter a valid email address")])
    submit = SubmitField('Send Reset Link')

#form for resetting password
class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', 
                            validators=[
                                DataRequired(message="Password is required"),
                                Length(min=8, message="Password must be at least 8 characters long")
                            ])
    confirm_password = PasswordField('Confirm New Password', 
                                    validators=[
                                        DataRequired(message="Confirm password is required"),
                                        EqualTo('password', message="Passwords must match")
                                    ])
    submit = SubmitField('Reset Password')

#Buy now form
class BuyNowForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    payment_method = RadioField('Payment Method', choices=[('cod', 'Cash On Delivery'), ('paypal', 'Paypal (unavailable)'), ('bank', 'Bank Transfer (unavailable)')], validators=[DataRequired()])
    submit = SubmitField('Buy Now')