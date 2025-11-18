from flask import Flask , render_template , redirect , session, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask import request
import os


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///purchases.db"
db = SQLAlchemy(app)

print(os.path.abspath("purchases.db"))

class Purchase(db.Model):
    id = db.Column(db.Integer , primary_key = True)
    name = db.Column(db.String , nullable = False )
    quantity = db.Column(db.Integer, default = 1)
    price = db.Column(db.Float , nullable = False )
    category = db.Column(db.String)
    date = db.Column(db.DateTime , default = datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer , primary_key = True)
    email = db.Column(db.String , nullable = False )
    password = db.Column(db.String , nullable = False )
    purchases = db.relationship("Purchase", backref="user", lazy=True)


app.secret_key = "abc123"

@app.route("/")
def home():
    return "Hello!"


@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "GET":
        return render_template("Register.htm")
    else:
        email = request.form["email"]
        password = request.form["password"]
        password2 = request.form["password2"]
        if password == password2:
            user = User(email=email, password=password)
            db.session.add(user)
            db.session.commit()
            return redirect("/login")
        else:
            return "Wrong password"    

@app.route("/login", methods=["GET", "POST"])
def login_user():
    if request.method == "GET":
        return render_template("login.htm")
    else:
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email, password=password).first()

        if user:
            session["user_id"] = user.id
            return redirect("/profile")

        return "Wrong username or password"

@app.get("/profile")
def profile():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    purchases = Purchase.query.filter_by(user_id=user_id).all()

    return redirect("/purchases")

@app.route("/purchases")
def show_purchases():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    limit = int(request.args.get("limit", 5))
    user_purchases = Purchase.query.filter_by(user_id=user_id).order_by(Purchase.id.desc()).limit(limit).all() 
    return render_template("PersonalArea.htm", purchases=user_purchases,limit=limit)


@app.route("/add", methods=["GET", "POST"])
def add_purchase():
    if request.method == "POST":
        if "user_id" not in session:
           return redirect("/login")
        item = Purchase(
            name=request.form["name"],
            quantity=request.form["quantity"],
            price=request.form["price"],
            category=request.form["category"],
            user_id=session["user_id"]
        )
        db.session.add(item)
        db.session.commit()
        return redirect("/profile")
    return render_template("addPurchase.htm")

@app.route("/update/<int:purchase_id>", methods=["GET", "POST"])
def update_purchase(purchase_id):
    if "user_id" not in session:
        return redirect("/login")

    purchase = Purchase.query.filter_by(id=purchase_id, user_id=session["user_id"]).first()

    if not purchase:
        return "Purchase not found or you do not have permission"

    if request.method == "POST":
        print(request.form) 

        if "name" not in request.form:
            return "Form is missing fields. Check updatePurchase.htm"

        purchase.name = request.form.get("name")
        purchase.quantity = request.form.get("quantity")
        purchase.price = request.form.get("price")
        purchase.category = request.form.get("category")

        db.session.commit()
        return redirect("/purchases")

    return render_template("updatePurchase.htm", purchase=purchase)

@app.route("/delete/<int:purchase_id>", methods=["POST"])
def delete_purchase(purchase_id):
    purchase = Purchase.query.get(purchase_id)

    if not purchase:
        return "Purchase not found", 404

    db.session.delete(purchase)
    db.session.commit()
    
    return redirect("/profile")

@app.route("/more/<int:limit>")
def show_more(limit):
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]
    user_purchases = Purchase.query.filter_by(user_id=user_id).order_by(Purchase.id.desc()).limit(limit).all()
    return render_template("PersonalArea.htm", purchases=user_purchases, limit=limit)

def init_db():
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    init_db()
    app.run(debug=True)