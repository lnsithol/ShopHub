from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login import UserMixin, login_user, logout_user, login_required, current_user,  LoginManager
from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from werkzeug.utils import secure_filename
import uuid
import os

from flask_migrate import Migrate



# 1. Initialize our flask application
app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/myshop_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Avoids a warning
app.config['SECRET_KEY'] = 'my-super-secret-key'

# Create SQLAlchemy instance
db = SQLAlchemy(app)
migrate = Migrate(app, db)

import os

BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)

app.config['UPLOAD_FOLDER'] = os.path.join(
    BASE_DIR,
    'static',
    'uploads',
    'products'
)

app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.context_processor
def inject_user():
    return dict(current_user=current_user)

# Create User model
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    role = db.Column(
        db.String(20),
        default="customer"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.now
    )
     
    is_active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<User {self.username}>"
    

class Category(db.Model):

    __tablename__ = "categories"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    description = db.Column(
        db.Text
    )

    image = db.Column(
        db.String(255)
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    products = db.relationship(
        "Product",
        backref="category",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Category {self.name}>"

class Product(db.Model):

    __tablename__ = "products"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey('categories.id'),
        nullable=False
    )

    name = db.Column(
        db.String(200),
        nullable=False
    )

    sku = db.Column(
        db.String(100),
        unique=True
    )

    description = db.Column(
        db.Text
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    sale_price = db.Column(
        db.Float
    )

    stock_quantity = db.Column(
        db.Integer,
        default=0
    )
    image = db.Column(
    db.String(255),
    nullable=True
    )

    featured = db.Column(
        db.Boolean,
        default=False
    )

    status = db.Column(
        db.String(20),
        default="active"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )


class ProductImage(db.Model):

    __tablename__ = "product_images"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id")
    )

    image_path = db.Column(
        db.String(255)
    )

    is_primary = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# 2. Define route to home page
@app.route("/")
def home():
    return render_template("store/home.html")

from werkzeug.security import check_password_hash
from flask_login import login_user


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()
        password = request.form["password"]

        user = User.query.filter_by(
            email=email
        ).first()

        if not user:

            flash(
                "Account does not exist.",
                "danger"
            )

            return redirect(url_for("register"))

        if not check_password_hash(
            user.password_hash,
            password
        ):

            flash(
                "Incorrect password.",
                "danger"
            )

            return redirect(url_for("login"))

        login_user(user)

        flash(
            f"Welcome back, {user.username}!",
            "success"
        )

        return redirect(url_for("dashboard"))

    return render_template("auth/login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect(url_for("register"))

        username_exists = User.query.filter_by(
            username=username
        ).first()

        if username_exists:

            flash(
                "Username already exists.",
                "danger"
            )

            return redirect(url_for("register"))

        email_exists = User.query.filter_by(
            email=email
        ).first()

        if email_exists:

            flash(
                "Email already registered.",
                "danger"
            )

            return redirect(url_for("register"))

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )

        db.session.add(user)
        db.session.commit()

        flash(
            "Account created successfully.",
            "success"
        )

        return redirect(url_for("login"))

    return render_template("auth/register.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/dashboard")
@login_required
def dashboard():
    
    if (current_user.role == 'admin'):
        return render_template(
        "admin/dashboard.html", username='Guest'
    )
    else:
        return render_template(
        "customer/dashboard.html", username='Guest'
    )

@app.route('/admin/products')
@login_required
def admin_products():

    products = Product.query.order_by(
        Product.created_at.desc()
    ).all()

    return render_template(
        'admin/products/index.html',
        products=products
    )

@app.route(
    '/admin/products/create',
    methods=['GET', 'POST']
)
@login_required
def create_product():

    categories = Category.query.order_by(
        Category.name
    ).all()

    if request.method == "POST":
        image_filename = None

        image = request.files.get(
            'image'
        )

        if image and image.filename:

            extension = image.filename.split(
                '.'
            )[-1]

            image_filename = (
                str(uuid.uuid4())
                + '.'
                + extension
            )

            image.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    image_filename
                )
            )

            product = Product(

                category_id=request.form.get(
                    "category_id"
                ),

                name=request.form.get(
                    "name"
                ),

                description=request.form.get(
                    "description"
                ),

                sku=request.form.get(
                    "sku"
                ),

                price=request.form.get(
                    "price"
                ),

                stock_quantity=request.form.get(
                    "stock_quantity"
                ),

                image=image_filename,

                status=request.form.get(
                    "status"
                )

            )

        db.session.add(product)

        db.session.commit()

        flash(
            "Product created successfully",
            "success"
        )

        return redirect(
            url_for("admin_products")
        )

    return render_template(
        "admin/products/create.html",
        categories=categories
    )

@app.route(
    '/admin/products/edit/<int:id>',
    methods=['GET', 'POST']
)
@login_required
def edit_product(id):

    product = Product.query.get_or_404(id)

    categories = Category.query.all()

    if request.method == "POST":

        product.name = request.form.get(
            "name"
        )

        product.category_id = request.form.get(
            "category_id"
        )

        product.description = request.form.get(
            "description"
        )

        product.price = request.form.get(
            "price"
        )

        product.sale_price = request.form.get(
            "sale_price"
        )

        product.sku = request.form.get(
            "sku"
        )

        product.stock_quantity = request.form.get(
            "stock_quantity"
        )

        product.status = request.form.get(
            "status"
        )

        product.featured = True if request.form.get(
            "featured"
        ) else False

        db.session.commit()

        flash(
            "Product updated successfully",
            "success"
        )

        return redirect(
            url_for(
                'admin_products'
            )
        )

    return render_template(
        'admin/products/edit.html',
        product=product,
        categories=categories
    )


@app.route(
    '/admin/products/delete/<int:id>',
    methods=['GET', 'POST']
)
@login_required
def delete_product(id):

    product = Product.query.get_or_404(id)

    if request.method == "POST":

        db.session.delete(product)

        db.session.commit()

        flash(
            'Product deleted successfully',
            'success'
        )

        return redirect(
            url_for('admin_products')
        )

    return render_template(
        'admin/products/delete.html',
        product=product
    )


@app.route('/products')
def products():
    products = [

        {
            "id":1,
            "name":"Wireless Headphones",
            "price":99,
            "category":"Electronics",
            "image":"https://picsum.photos/400/300?1",
            "description":"Premium sound quality"
        },

        {
            "id":2,
            "name":"Smart Watch",
            "price":149,
            "category":"Electronics",
            "image":"https://picsum.photos/400/300?2",
            "description":"Track fitness and health"
        },

        {
            "id":3,
            "name":"Running Shoes",
            "price":89,
            "category":"Sports",
            "image":"https://picsum.photos/400/300?3",
            "description":"Comfortable and durable"
        }

    ]

    return render_template(
        'store/products.html',
        products=products
    )


@app.route("/product_detail")
def product_detail():
    return render_template("store/product_detail.html")
@app.route('/admin/categories')
@login_required
def admin_categories():

    categories = Category.query.order_by(
        Category.name
    ).all()

    return render_template(
        'admin/categories/index.html',
        categories=categories
    )


@app.route(
    '/admin/categories/create',
    methods=['GET', 'POST']
)
@login_required
def create_category():

    if request.method == 'POST':

        category = Category(

            name=request.form.get('name'),

            description=request.form.get(
                'description'
            )

        )

        db.session.add(category)

        db.session.commit()

        flash(
            'Category created successfully',
            'success'
        )

        return redirect(
            url_for(
                'admin_categories'
            )
        )

    return render_template(
        'admin/categories/create.html'
    )


@app.route(
    '/admin/categories/edit/<int:id>',
    methods=['GET', 'POST']
)
@login_required
def edit_category(id):

    category = Category.query.get_or_404(id)

    if request.method == 'POST':

        category.name = request.form.get(
            'name'
        )

        category.description = request.form.get(
            'description'
        )

        db.session.commit()

        flash(
            'Category updated',
            'success'
        )

        return redirect(
            url_for(
                'admin_categories'
            )
        )

    return render_template(
        'admin/categories/edit.html',
        category=category
    )


@app.route(
    '/admin/categories/delete/<int:id>'
)
@login_required
def delete_category(id):

    category = Category.query.get_or_404(id)

    db.session.delete(category)

    db.session.commit()

    flash(
        'Category deleted',
        'success'
    )

    return redirect(
        url_for(
            'admin_categories'
        )
    )
if __name__ == "__main__":
    with app.app_context():
        try:
            db.create_all()
        except Exception as database_exception:
            print(f"An unexpected error occurred: {database_exception}")
    app.run(debug=True)