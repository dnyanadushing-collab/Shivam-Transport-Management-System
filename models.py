from extensions import db


# ---------------- USER ----------------

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)


# ---------------- CUSTOMER ----------------

class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), unique=True)
    village = db.Column(db.String(100))
    address = db.Column(db.Text)

    trips = db.relationship(
        "Trip",
        back_populates="customer"
    )

    def __repr__(self):
        return f"<Customer {self.name}>"


# ---------------- TRIP ----------------

class Trip(db.Model):
    __tablename__ = "trips"

    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False
    )

    customer = db.relationship(
        "Customer",
        back_populates="trips"
    )

    vehicle_no = db.Column(db.String(30))
    from_place = db.Column(db.String(100))
    to_place = db.Column(db.String(100))
    material = db.Column(db.String(100))
    weight = db.Column(db.Float)

    amount = db.Column(db.Float)
    advance = db.Column(db.Float)
    balance = db.Column(db.Float)

    trip_date = db.Column(db.String(20))


# ---------------- UDHARI ----------------

class Udhari(db.Model):
    __tablename__ = "udhari"

    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False
    )

    customer = db.relationship("Customer")

    amount = db.Column(db.Float, nullable=False)

    description = db.Column(db.String(200))

    udhari_date = db.Column(db.String(20))


# ---------------- PAYMENT ----------------

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customers.id"),
        nullable=False
    )

    customer = db.relationship("Customer")

    amount = db.Column(db.Float, nullable=False)

    payment_mode = db.Column(db.String(50))

    remarks = db.Column(db.String(200))

    payment_date = db.Column(db.String(20))

    # ---------------- EXPENSE ----------------

class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)

    expense_type = db.Column(db.String(100), nullable=False)

    vehicle = db.Column(db.String(100))

    amount = db.Column(db.Float, nullable=False)

    description = db.Column(db.String(300))

    expense_date = db.Column(db.String(20))