from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_mail import Mail, Message
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Fundraising database
fundraising_db_path = "fundraising.db"
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{fundraising_db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
fund_db = SQLAlchemy(app)

# Contact messages database
messages_db_path = "messages.db"
messages_app = Flask(__name__)
messages_app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{messages_db_path}"
messages_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
messages_db = SQLAlchemy(messages_app)

# Flask mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'ecosphereofficial.ph@gmail.com'
app.config['MAIL_PASSWORD'] = 'dyig yire yngw fnoj'
app.config['MAIL_DEFAULT_SENDER'] = ('EcoSphere', 'ecosphereofficial.ph@gmail.com')
mail = Mail(app)

FUNDRAISING_GOAL = 1000000000

# Helper function
def generate_reference_code():
    return "ECO-" + uuid.uuid4().hex[:10].upper()

# Fundraising models
class User(fund_db.Model):
    id = fund_db.Column(fund_db.Integer, primary_key=True)
    firstname = fund_db.Column(fund_db.String(50), nullable=False)
    lastname = fund_db.Column(fund_db.String(50), nullable=False)
    contact = fund_db.Column(fund_db.String(15), unique=True, nullable=False)
    email = fund_db.Column(fund_db.String(100), unique=True, nullable=False)
    transactions = fund_db.relationship('Transaction', backref='user', lazy=True)
    emails = fund_db.relationship('Email', backref='user', lazy=True)

class Transaction(fund_db.Model):
    id = fund_db.Column(fund_db.Integer, primary_key=True)
    user_id = fund_db.Column(fund_db.Integer, fund_db.ForeignKey('user.id'), nullable=False)
    amount = fund_db.Column(fund_db.Float, nullable=False)
    mode_of_payment = fund_db.Column(fund_db.String(20), nullable=False)
    transaction_number = fund_db.Column(fund_db.String(50), unique=True, nullable=False)
    reference_number = fund_db.Column(fund_db.String(50), unique=True, nullable=False)
    created_at = fund_db.Column(fund_db.DateTime, default=datetime.utcnow)
    emails = fund_db.relationship('Email', backref='transaction', lazy=True)

class Email(fund_db.Model):
    id = fund_db.Column(fund_db.Integer, primary_key=True)
    user_id = fund_db.Column(fund_db.Integer, fund_db.ForeignKey('user.id'), nullable=False)
    transaction_id = fund_db.Column(fund_db.Integer, fund_db.ForeignKey('transaction.id'), nullable=False)
    sent_at = fund_db.Column(fund_db.DateTime, default=datetime.utcnow)
    status = fund_db.Column(fund_db.String(10), nullable=False)

# Messages model
class MessageDB(messages_db.Model):
    id = messages_db.Column(messages_db.Integer, primary_key=True)
    name = messages_db.Column(messages_db.String(100), nullable=False)
    email = messages_db.Column(messages_db.String(100), nullable=False)
    phone = messages_db.Column(messages_db.String(20))
    subject = messages_db.Column(messages_db.String(200), nullable=False)
    message = messages_db.Column(messages_db.Text, nullable=False)

# Create databases
with app.app_context():
    fund_db.create_all()

with messages_app.app_context():
    messages_db.create_all()

# Static pages
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/sdg')
def sdg():
    return render_template('sdg.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/team')
def team():
    return render_template('team.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/organizations')
def organizations():
    return render_template('org.html')

# Contact form route
@app.route("/send_message", methods=["POST"])
def send_message():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    phone = request.form.get("phone", "").strip()
    subject = request.form.get("subject", "").strip()
    message_text = request.form.get("message", "").strip()

    if not name or not email or not subject or not message_text:
        flash("Please fill out all required fields!", "error")
        return redirect(url_for("contact") + "#Contacts")

    new_msg = MessageDB(
        name=name,
        email=email,
        phone=phone,
        subject=subject,
        message=message_text
    )

    with messages_app.app_context():
        messages_db.session.add(new_msg)
        messages_db.session.commit()

    flash("Your message has been sent successfully!", "success")
    return redirect(url_for("contact") + "#Contacts")

# Fundraising / donation route
@app.route("/donation", methods=["GET", "POST"])
def donation():
    if request.method == "POST":
        try:
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            contact = request.form['contact']
            email = request.form['email']
            amount = float(request.form['amount'])
            payment_mode = request.form['payment_mode']
            transaction_number = request.form.get('transaction_number', '').strip()

            if not transaction_number:
                return jsonify({"success": False, "error": "Transaction number is required."})

            user = User.query.filter((User.email == email) | (User.contact == contact)).first()
            if not user:
                user = User(firstname=first_name, lastname=last_name, contact=contact, email=email)
                fund_db.session.add(user)
                fund_db.session.commit()
            else:
                user.firstname = first_name
                user.lastname = last_name
                fund_db.session.commit()

            reference_code = generate_reference_code()

            transaction = Transaction(
                user_id=user.id,
                amount=amount,
                mode_of_payment=payment_mode,
                transaction_number=transaction_number,
                reference_number=reference_code
            )
            fund_db.session.add(transaction)
            fund_db.session.commit()

            # Send email
            email_status = "failed"
            try:
                msg = Message(
                    subject="Thank You for Supporting EcoSphere!",
                    recipients=[email]
                )
                msg.html = f"""
                <html>
                <body style="font-family: 'Outfit', sans-serif; color: #1a1a1a; line-height:1.6;">
                    <h2>Hi {first_name} {last_name},</h2>
                    <p>Thank you for your donation of <strong>₱{amount}</strong> via <strong>{payment_mode}</strong>.</p>
                    <p><strong>Your Transaction Details:</strong></p>
                    <p>Transaction Number: <strong>{transaction_number}</strong></p>
                    <p>EcoSphere Reference Code: <strong>{reference_code}</strong></p>
                    <p>Your support helps fund sustainable projects and climate initiatives. 🌿</p>
                    <p>Warm regards,<br>The EcoSphere Team</p>
                </body>
                </html>
                """
                mail.send(msg)
                email_status = "sent"
            except Exception as e:
                print("Email sending failed:", e)

            email_record = Email(user_id=user.id, transaction_id=transaction.id, status=email_status)
            fund_db.session.add(email_record)
            fund_db.session.commit()

            return jsonify({"success": True, "donation_id": transaction.id})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

    total_amount = fund_db.session.query(func.sum(Transaction.amount)).scalar() or 0
    total_count = fund_db.session.query(func.count(Transaction.id)).scalar() or 0
    recent_donors = Transaction.query.order_by(Transaction.id.desc()).limit(5).all()
    progress = min(total_amount / FUNDRAISING_GOAL * 100, 100)

    return render_template(
        "fundraising.html",
        total_amount=total_amount,
        total_count=total_count,
        recent_donors=recent_donors,
        progress=progress,
        goal=FUNDRAISING_GOAL
    )

# Payment instructions
@app.route("/payment/<int:transaction_id>")
def payment(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    return render_template("payment.html", donation=transaction)

# Run app
if __name__ == "__main__":
    app.run(debug=True)