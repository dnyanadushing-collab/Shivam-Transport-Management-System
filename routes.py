from flask import Blueprint, render_template, request, redirect, url_for
from extensions import db
from models import User, Customer

auth = Blueprint("auth", __name__)

# ---------------- Login ----------------

@auth.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:
            return redirect(url_for("auth.dashboard"))

        return "Invalid Username or Password"

    return render_template("login.html")


# ---------------- Dashboard ----------------

@auth.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# ---------------- Customers ----------------

@auth.route("/customers")
def customers():
    return render_template("customers.html")


# ---------------- Add Customer ----------------

@auth.route("/add_customer", methods=["GET", "POST"])
def add_customer():

    if request.method == "POST":

        customer = Customer(
            name=request.form["name"],
            mobile=request.form["mobile"],
            village=request.form["village"],
            address=request.form["address"]
        )

        db.session.add(customer)
        db.session.commit()

        return redirect(url_for("auth.customers"))

    return render_template("add_customer.html")