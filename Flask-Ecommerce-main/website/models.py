from . import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import secrets

# Define the models for the database
# The models are classes that inherit from db.Model
# Each class represents a table in the database
# Each attribute in the class represents a column in the table
# The __str__ method is used to represent the object in a readable format

#Customer Database
class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String(150))
    is_verified = db.Column(db.Integer, default = 0)
    date_joined = db.Column(db.DateTime(), default=datetime.utcnow)
    seller_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    address = db.Column(db.String(200))
    bir_number = db.Column(db.Integer)
    valid_id = db.Column(db.String)
    google_id = db.Column(db.String(150))
    profile_picture = db.Column(db.String(120)) 
    phone_number = db.Column(db.Integer)
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiration = db.Column(db.DateTime, nullable=True)

    cart_items = db.relationship('Cart', backref=db.backref('customer', lazy=True))
    orders = db.relationship('Order', backref=db.backref('customer', lazy=True))

    @property
    def password(self):
        raise AttributeError('Password is not a readable Attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password=password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password=password)

    def __str__(self):
        return '<Customer %r>' % Customer.id

#Product Database
class Product(db.Model):
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    previous_price = db.Column(db.Float, nullable=False)
    in_stock = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(200))
    product_picture = db.Column(db.String(1000), nullable=False)
    flash_sale = db.Column(db.Boolean, default=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String)
    archived = db.Column(db.Integer, default=0)

    carts = db.relationship('Cart', backref=db.backref('product', lazy=True))
    orders = db.relationship('Order', backref=db.backref('product', lazy=True))

    def __str__(self):
        return '<Product %r>' % self.product_name

#Cart Database
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    is_selected = db.Column(db.Integer, default=0)

    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    # customer product

    def __str__(self):
        return '<Cart %r>' % self.id

#Order Database
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(100), nullable=False)
    payment_id = db.Column(db.String(1000), nullable=False)

    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    # customer

    def __str__(self):
        return '<Order %r>' % self.id

#Wishlist Database
class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    customer_link = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_link = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)

    # Establish relationship with the Product model
    product = db.relationship('Product', backref='wishlist_items')

    def __str__(self):
        return '<Wishlist %r>' % self.id

#Review Database
class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)  # Changed to customer_id
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)    # Changed to product_id
    review_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    product = db.relationship('Product', backref='product_reviews', foreign_keys=[product_id])
    customer = db.relationship('Customer', backref='customer_reviews', foreign_keys=[customer_id])

    def __str__(self):
        return f'<Review {self.id} - Product {self.product_id} - Customer {self.customer_id}>'

