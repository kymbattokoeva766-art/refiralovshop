from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import secrets
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nft_shop_key_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    unique_code = db.Column(db.String(20), unique=True, nullable=False)
    amount = db.Column(db.String(50), default="5 NFT (Тортики)")
    buyer_contact = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default="pending") 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

def generate_code():
    chars = string.ascii_uppercase + string.digits
    return f"{''.join(secrets.choice(chars) for _ in range(3))}-{''.join(secrets.choice(chars) for _ in range(3))}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buy/<product_name>', methods=['POST'])
def buy(product_name):
    code = generate_code()
    new_order = Order(product_name=product_name, unique_code=code)
    db.session.add(new_order)
    db.session.commit()
    return redirect(url_for('payment', code=code))

@app.route('/payment/<code>', methods=['GET', 'POST'])
def payment(code):
    order = Order.query.filter_by(unique_code=code).first_or_404()
    if request.method == 'POST':
        contact = request.form.get('contact')
        # Если юзер забыл @, добавим сами
        if contact and not contact.startswith('@'):
            contact = '@' + contact
        order.buyer_contact = contact
        db.session.commit()
        return render_template('payment.html', order=order, success=True)
    return render_template('payment.html', order=order, success=False)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == 'admin123':
            session['admin_logged_in'] = True
    if not session.get('admin_logged_in'):
        return render_template('admin.html', logged_in=False)
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin.html', logged_in=True, orders=orders)

@app.route('/admin/action/<int:order_id>/<action>')
def admin_action(order_id, action):
    if not session.get('admin_logged_in'): return redirect(url_for('admin'))
    order = Order.query.get_or_404(order_id)
    order.status = 'paid' if action == 'approve' else 'rejected'
    db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
