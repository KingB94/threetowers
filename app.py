from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import stripe

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management

# Load Stripe secret key securely from environment variables
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
if not stripe.api_key:
    app.logger.error("Stripe secret key not set. Please set the STRIPE_SECRET_KEY environment variable.")

# Example pricing function
def calculate_price(countries, segments):
    base_price = 100  # Base price in USD
    country_multiplier = len(countries) * 10  # $10 per country
    segment_multiplier = len(segments) * 20   # $20 per segment
    return base_price + country_multiplier + segment_multiplier

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/pricing")
def pricing():
    return render_template("pricing.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # This is a dummy example. In a real app, you'd verify user credentials.
        session["logged_in"] = True
        session["user"] = request.form.get("username", "User")  # Store username if needed
        return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Process sign up logic
        session["logged_in"] = True
        session["user"] = request.form.get("username", "User")
        return redirect(url_for("index"))
    return render_template("signup.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/services")
def services():
    return render_template("services.html")

@app.route("/how_it_works")
def how_it_works():
    return render_template("how_it_works.html")

@app.route("/testimonials")
def testimonials():
    return render_template("testimonials.html")

@app.route("/imprint")
def imprint():
    return render_template("imprint.html")

@app.route("/account")
def account():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("account.html", user=session.get("user"))

@app.route("/get_price", methods=["POST"])
def get_price():
    try:
        data = request.get_json()
        countries = data.get("countries", [])
        segments = data.get("segments", [])
        price = calculate_price(countries, segments)
        return jsonify({"price": price})
    except Exception as e:
        app.logger.exception("Error in get_price")
        return jsonify({"error": str(e)}), 400

@app.route("/create_checkout_session", methods=["POST"])
def create_checkout_session():
    try:
        data = request.get_json()
        price = float(data.get("price", 0))
        if price <= 0:
            raise ValueError("Invalid price")
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": "Software Subscription"},
                        "unit_amount": int(price * 100),  # convert dollars to cents
                    },
                    "quantity": 1,
                },
            ],
            mode="payment",
            success_url="https://yourwebsite.com/success",
            cancel_url="https://threetowers.onrender.com/",
        )
        return jsonify({"sessionId": checkout_session.id})
    except Exception as e:
        app.logger.exception("Error in create_checkout_session")
        return jsonify({"error": str(e)}), 400

@app.route("/create_payment_intent", methods=["POST"])
def create_payment_intent():
    try:
        data = request.get_json()
        price = float(data.get("price", 0))
        if price <= 0:
            raise ValueError("Invalid price")
        payment_intent = stripe.PaymentIntent.create(
            amount=int(price * 100),
            currency="usd",
            payment_method_types=["card"],
        )
        return jsonify({"clientSecret": payment_intent.client_secret})
    except Exception as e:
        app.logger.exception("Error in create_payment_intent")
        return jsonify({"error": str(e)}), 400

@app.route("/create_paypal_order", methods=["POST"])
def create_paypal_order():
    try:
        data = request.get_json()
        price = float(data.get("price", 0))
        if price <= 0:
            raise ValueError("Invalid price")
        order_id = "SIMULATED_PAYPAL_ORDER_ID"
        return jsonify({"orderID": order_id})
    except Exception as e:
        app.logger.exception("Error in create_paypal_order")
        return jsonify({"error": str(e)}), 400

@app.route("/capture_paypal_order", methods=["POST"])
def capture_paypal_order():
    try:
        data = request.get_json()
        order_id = data.get("orderID")
        if not order_id:
            raise ValueError("Missing order ID")
        return jsonify({"status": "COMPLETED"})
    except Exception as e:
        app.logger.exception("Error in capture_paypal_order")
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
