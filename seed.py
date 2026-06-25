from app import app
from app import db

from app import Category
from app import Product


with app.app_context():

    electronics = Category(
        name="Electronics"
    )

    fashion = Category(
        name="Fashion"
    )

    db.session.add_all([
        electronics,
        fashion
    ])

    db.session.commit()

    p1 = Product(
        category_id=electronics.id,
        name="Wireless Headphones",
        sku="ELEC001",
        price=899.99,
        stock_quantity=20
    )

    p2 = Product(
        category_id=electronics.id,
        name="Smart Watch",
        sku="ELEC002",
        price=1299.99,
        stock_quantity=10
    )

    p3 = Product(
        category_id=fashion.id,
        name="Men T-Shirt",
        sku="FASH001",
        price=199.99,
        stock_quantity=50
    )

    db.session.add_all([
        p1,
        p2,
        p3
    ])

    db.session.commit()

    print("Seed complete")