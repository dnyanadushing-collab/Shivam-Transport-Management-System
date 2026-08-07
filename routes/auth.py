from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    make_response
)

from sqlalchemy import func, or_
from urllib.parse import quote
from io import BytesIO

from openpyxl import Workbook

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle
)

from extensions import db

from models import (
    User,
    Customer,
    Trip,
    Udhari,
    Payment
)

auth = Blueprint("auth", __name__)


# ---------------- LOGIN ----------------

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


# ---------------- DASHBOARD ----------------

@auth.route("/dashboard")
def dashboard():

    total_customers = Customer.query.count()

    total_trips = Trip.query.count()

    total_udhari = db.session.query(
        func.coalesce(func.sum(Udhari.amount), 0)
    ).scalar()

    total_payments = db.session.query(
        func.coalesce(func.sum(Payment.amount), 0)
    ).scalar()

    remaining_balance = total_udhari - total_payments

    return render_template(
        "dashboard.html",
        total_customers=total_customers,
        total_trips=total_trips,
        total_udhari=total_udhari,
        total_payments=total_payments,
        remaining_balance=remaining_balance
    )


# ---------------- CUSTOMERS ----------------

@auth.route("/customers")
def customers():

    search = request.args.get("search", "")

    if search:

        customers = Customer.query.filter(
            Customer.name.ilike(f"%{search}%")
        ).all()

    else:

        customers = Customer.query.all()

    return render_template(
        "customers.html",
        customers=customers,
        search=search
    )


# ---------------- ADD CUSTOMER ----------------

@auth.route("/add_customer", methods=["GET", "POST"])
def add_customer():

    if request.method == "POST":

        existing = Customer.query.filter_by(
            mobile=request.form["mobile"]
        ).first()

        if existing:

            return render_template(
                "add_customer.html",
                error="Mobile number already exists."
            )

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


# ---------------- EDIT CUSTOMER ----------------

@auth.route("/edit_customer/<int:id>", methods=["GET", "POST"])
def edit_customer(id):

    customer = Customer.query.get_or_404(id)

    if request.method == "POST":

        customer.name = request.form["name"]
        customer.mobile = request.form["mobile"]
        customer.village = request.form["village"]
        customer.address = request.form["address"]

        db.session.commit()

        return redirect(url_for("auth.customers"))

    return render_template(
        "edit_customer.html",
        customer=customer
    )


# ---------------- DELETE CUSTOMER ----------------

@auth.route("/delete_customer/<int:id>")
def delete_customer(id):

    customer = Customer.query.get_or_404(id)

    db.session.delete(customer)
    db.session.commit()

    return redirect(url_for("auth.customers"))

# ---------------- TRIPS ----------------

@auth.route("/trips")
def trips():

    search = request.args.get("search", "")
    from_date = request.args.get("from_date", "")
    to_date = request.args.get("to_date", "")

    query = Trip.query.join(Customer)

    if search:
        query = query.filter(
            or_(
                Customer.name.ilike(f"%{search}%"),
                Trip.vehicle_no.ilike(f"%{search}%"),
                Trip.material.ilike(f"%{search}%"),
                Trip.from_place.ilike(f"%{search}%"),
                Trip.to_place.ilike(f"%{search}%")
            )
        )

    if from_date:
        query = query.filter(Trip.trip_date >= from_date)

    if to_date:
        query = query.filter(Trip.trip_date <= to_date)

    trips = query.all()

    return render_template(
        "trips.html",
        trips=trips,
        search=search,
        from_date=from_date,
        to_date=to_date
    )


# ---------------- ADD TRIP ----------------

@auth.route("/add_trip", methods=["GET", "POST"])
def add_trip():

    customers = Customer.query.all()

    if request.method == "POST":

        trip = Trip(
            customer_id=int(request.form["customer"]),
            vehicle_no=request.form["vehicle"],
            from_place=request.form["from_place"],
            to_place=request.form["to_place"],
            material=request.form["material"],
            weight=request.form["weight"],
            amount=request.form["amount"],
            advance=request.form["advance"],
            balance=request.form["balance"],
            trip_date=request.form["trip_date"]
        )

        db.session.add(trip)
        db.session.commit()

        return redirect(url_for("auth.trips"))

    return render_template(
        "add_trip.html",
        customers=customers
    )


# ---------------- EDIT TRIP ----------------

@auth.route("/edit_trip/<int:id>", methods=["GET", "POST"])
def edit_trip(id):

    trip = Trip.query.get_or_404(id)
    customers = Customer.query.all()

    if request.method == "POST":

        trip.customer_id = int(request.form["customer"])
        trip.vehicle_no = request.form["vehicle"]
        trip.from_place = request.form["from_place"]
        trip.to_place = request.form["to_place"]
        trip.material = request.form["material"]
        trip.weight = request.form["weight"]
        trip.amount = request.form["amount"]
        trip.advance = request.form["advance"]
        trip.balance = request.form["balance"]
        trip.trip_date = request.form["trip_date"]

        db.session.commit()

        return redirect(url_for("auth.trips"))

    return render_template(
        "edit_trip.html",
        trip=trip,
        customers=customers
    )


# ---------------- DELETE TRIP ----------------

@auth.route("/delete_trip/<int:id>")
def delete_trip(id):

    trip = Trip.query.get_or_404(id)

    db.session.delete(trip)
    db.session.commit()

    return redirect(url_for("auth.trips"))


# ---------------- TEST ----------------

@auth.route("/test")
def test():
    return "TEST ROUTE WORKING"

# ---------------- UDHARI ----------------

@auth.route("/udhari")
def udhari():

    search = request.args.get("search", "")

    if search:

        udhari_list = Udhari.query.join(Customer).filter(
            Customer.name.ilike(f"%{search}%")
        ).all()

    else:

        udhari_list = Udhari.query.all()

    return render_template(
        "udhari.html",
        udhari_list=udhari_list,
        search=search
    )


# ---------------- ADD UDHARI ----------------

@auth.route("/add_udhari", methods=["GET", "POST"])
def add_udhari():

    customers = Customer.query.all()

    if request.method == "POST":

        udhari = Udhari(
            customer_id=int(request.form["customer"]),
            amount=request.form["amount"],
            description=request.form["description"],
            udhari_date=request.form["udhari_date"]
        )

        db.session.add(udhari)
        db.session.commit()

        return redirect(url_for("auth.udhari"))

    return render_template(
        "add_udhari.html",
        customers=customers
    )


# ---------------- EDIT UDHARI ----------------

@auth.route("/edit_udhari/<int:id>", methods=["GET", "POST"])
def edit_udhari(id):

    udhari = Udhari.query.get_or_404(id)
    customers = Customer.query.all()

    if request.method == "POST":

        udhari.customer_id = int(request.form["customer"])
        udhari.amount = request.form["amount"]
        udhari.description = request.form["description"]
        udhari.udhari_date = request.form["udhari_date"]

        db.session.commit()

        return redirect(url_for("auth.udhari"))

    return render_template(
        "edit_udhari.html",
        udhari=udhari,
        customers=customers
    )


# ---------------- DELETE UDHARI ----------------

@auth.route("/delete_udhari/<int:id>")
def delete_udhari(id):

    udhari = Udhari.query.get_or_404(id)

    db.session.delete(udhari)
    db.session.commit()

    return redirect(url_for("auth.udhari"))


# ---------------- PAYMENTS ----------------

@auth.route("/payments")
def payments():

    search = request.args.get("search", "")

    if search:

        payments = Payment.query.join(Customer).filter(
            Customer.name.ilike(f"%{search}%")
        ).all()

    else:

        payments = Payment.query.all()

    return render_template(
        "payments.html",
        payments=payments,
        search=search
    )

# ---------------- ADD PAYMENT ----------------

@auth.route("/add_payment", methods=["GET", "POST"])
def add_payment():

    customers = Customer.query.all()

    if request.method == "POST":

        payment = Payment(
            customer_id=int(request.form["customer"]),
            amount=request.form["amount"],
            payment_mode=request.form["payment_mode"],
            remarks=request.form["remarks"],
            payment_date=request.form["payment_date"]
        )

        db.session.add(payment)
        db.session.commit()

        return redirect(url_for("auth.payments"))

    return render_template(
        "add_payment.html",
        customers=customers
    )


# ---------------- EDIT PAYMENT ----------------

@auth.route("/edit_payment/<int:id>", methods=["GET", "POST"])
def edit_payment(id):

    payment = Payment.query.get_or_404(id)
    customers = Customer.query.all()

    if request.method == "POST":

        payment.customer_id = int(request.form["customer"])
        payment.amount = request.form["amount"]
        payment.payment_mode = request.form["payment_mode"]
        payment.remarks = request.form["remarks"]
        payment.payment_date = request.form["payment_date"]

        db.session.commit()

        return redirect(url_for("auth.payments"))

    return render_template(
        "edit_payment.html",
        payment=payment,
        customers=customers
    )


# ---------------- DELETE PAYMENT ----------------

@auth.route("/delete_payment/<int:id>")
def delete_payment(id):

    payment = Payment.query.get_or_404(id)

    db.session.delete(payment)
    db.session.commit()

    return redirect(url_for("auth.payments"))


# ---------------- REPORTS ----------------

@auth.route("/reports")
def reports():

    total_customers = Customer.query.count()

    total_trips = Trip.query.count()

    total_udhari = db.session.query(
        func.coalesce(func.sum(Udhari.amount), 0)
    ).scalar()

    total_payments = db.session.query(
        func.coalesce(func.sum(Payment.amount), 0)
    ).scalar()

    remaining = total_udhari - total_payments

    return render_template(
        "reports.html",
        total_customers=total_customers,
        total_trips=total_trips,
        total_udhari=total_udhari,
        total_payments=total_payments,
        remaining=remaining
    )
# ---------------- EXCEL REPORT ----------------

@auth.route("/report/excel")
def report_excel():

    wb = Workbook()

    ws = wb.active

    ws.title = "Shivam Transport Report"

    ws.append(["Report", "Value"])

    ws.append(["Total Customers", Customer.query.count()])
    ws.append(["Total Trips", Trip.query.count()])

    total_udhari = db.session.query(
        func.coalesce(func.sum(Udhari.amount), 0)
    ).scalar()

    total_payments = db.session.query(
        func.coalesce(func.sum(Payment.amount), 0)
    ).scalar()

    remaining = total_udhari - total_payments

    ws.append(["Total Udhari", total_udhari])
    ws.append(["Total Payments", total_payments])
    ws.append(["Remaining Balance", remaining])

    output = BytesIO()

    wb.save(output)

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="Shivam_Transport_Report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
# ---------------- PDF REPORT ----------------

@auth.route("/report/pdf")
def report_pdf():

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    elements = []

    styles = getSampleStyleSheet()

    elements.append(
        Paragraph(
            "<b>🚛 Shivam Transport Report</b>",
            styles["Title"]
        )
    )

    data = [
        ["Report", "Value"],
        ["Total Customers", str(Customer.query.count())],
        ["Total Trips", str(Trip.query.count())],
        ["Total Udhari", f"₹ {db.session.query(func.coalesce(func.sum(Udhari.amount),0)).scalar()}"],
        ["Total Payments", f"₹ {db.session.query(func.coalesce(func.sum(Payment.amount),0)).scalar()}"]
    ]

    table = Table(data)

    table.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,0),colors.darkblue),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),

        ("GRID",(0,0),(-1,-1),1,colors.black),

        ("BACKGROUND",(0,1),(-1,-1),colors.beige),

        ("ALIGN",(0,0),(-1,-1),"CENTER"),

        ("BOTTOMPADDING",(0,0),(-1,0),10),

    ]))

    elements.append(table)

    doc.build(elements)

    pdf = buffer.getvalue()

    buffer.close()

    response = make_response(pdf)

    response.headers["Content-Type"] = "application/pdf"

    response.headers["Content-Disposition"] = "attachment; filename=Shivam_Transport_Report.pdf"

    return response

# ---------------- CUSTOMER LEDGER ----------------

@auth.route("/customer_ledger/<int:customer_id>")
def customer_ledger(customer_id):

    customer = Customer.query.get_or_404(customer_id)

    trips = Trip.query.filter_by(
        customer_id=customer_id
    ).order_by(Trip.id.desc()).all()

    udhari = Udhari.query.filter_by(
        customer_id=customer_id
    ).order_by(Udhari.id.desc()).all()

    payments = Payment.query.filter_by(
        customer_id=customer_id
    ).order_by(Payment.id.desc()).all()

    total_udhari = db.session.query(
        func.coalesce(func.sum(Udhari.amount), 0)
    ).filter(
        Udhari.customer_id == customer_id
    ).scalar()

    total_payment = db.session.query(
        func.coalesce(func.sum(Payment.amount), 0)
    ).filter(
        Payment.customer_id == customer_id
    ).scalar()

    remaining = total_udhari - total_payment

    return render_template(
        "customer_ledger.html",
        customer=customer,
        trips=trips,
        udhari=udhari,
        payments=payments,
        total_udhari=total_udhari,
        total_payment=total_payment,
        remaining=remaining
    )


# ---------------- CUSTOMER PDF ----------------

@auth.route("/customer_statement/<int:customer_id>")
def customer_statement(customer_id):

    customer = Customer.query.get_or_404(customer_id)

    trips = Trip.query.filter_by(customer_id=customer_id).all()

    udhari = Udhari.query.filter_by(customer_id=customer_id).all()

    payments = Payment.query.filter_by(customer_id=customer_id).all()

    total_udhari = db.session.query(
        func.coalesce(func.sum(Udhari.amount), 0)
    ).filter(
        Udhari.customer_id == customer_id
    ).scalar()

    total_payment = db.session.query(
        func.coalesce(func.sum(Payment.amount), 0)
    ).filter(
        Payment.customer_id == customer_id
    ).scalar()

    remaining = total_udhari - total_payment

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("<b>🚛 SHIVAM TRANSPORT</b>", styles["Title"])
    )

    elements.append(Paragraph("<br/>", styles["Normal"]))

    elements.append(
        Paragraph(f"<b>Customer :</b> {customer.name}", styles["Heading2"])
    )

    elements.append(
        Paragraph(f"<b>Mobile :</b> {customer.mobile}", styles["Normal"])
    )

    elements.append(
        Paragraph(f"<b>Village :</b> {customer.village}", styles["Normal"])
    )

    elements.append(Paragraph("<br/>", styles["Normal"]))

    data = [
        ["Particular", "Amount"],
        ["Total Udhari", f"Rs. {total_udhari}"],
        ["Total Payment", f"Rs. {total_payment}"],
        ["Remaining", f"Rs. {remaining}"]
    ]

    table = Table(data)

    table.setStyle(TableStyle([

        ("BACKGROUND", (0,0), (-1,0), colors.darkblue),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,1), (-1,-1), colors.beige),
        ("ALIGN", (0,0), (-1,-1), "CENTER")

    ]))

    elements.append(table)

    doc.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{customer.name}_Statement.pdf",
        mimetype="application/pdf"
    )
# ---------------- SEND WHATSAPP ----------------

@auth.route("/send_whatsapp/<int:customer_id>")
def send_whatsapp(customer_id):

    customer = Customer.query.get_or_404(customer_id)

    total_udhari = db.session.query(
        func.coalesce(func.sum(Udhari.amount), 0)
    ).filter(
        Udhari.customer_id == customer_id
    ).scalar()

    total_payment = db.session.query(
        func.coalesce(func.sum(Payment.amount), 0)
    ).filter(
        Payment.customer_id == customer_id
    ).scalar()

    remaining = total_udhari - total_payment

    message = f"""
🚛 Shivam Transport

Customer : {customer.name}

Total Udhari : Rs. {total_udhari}

Total Payment : Rs. {total_payment}

Remaining Balance : Rs. {remaining}

Thank You 🙏
"""

    mobile = customer.mobile

    url = "https://wa.me/91{}?text={}".format(
        mobile,
        quote(message)
    )

    return redirect(url)