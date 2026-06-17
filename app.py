from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login import UserMixin, login_user, logout_user, login_required, current_user,  LoginManager
from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 1. Initialize our flask application
app = Flask(__name__)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/myshop_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Avoids a warning
app.config['SECRET_KEY'] = 'my-super-secret-key'

# Create SQLAlchemy instance
db = SQLAlchemy(app)

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
        default=datetime.utcnow
    )

    def __repr__(self):
        return f"<User {self.username}>"

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

@app.route("/dashboard")
@login_required
def dashboard():

    return render_template(
        "customer/dashboard.html", username='Guest'
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
# @app.route("/dashboard")
# def dashboard():
#     if session ==  True:
#         redirect(url_for("home"))
#     else:
#         redirect(url_for("login"))

# 6. Run application
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)