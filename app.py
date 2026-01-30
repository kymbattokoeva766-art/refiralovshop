from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import uuid
import os
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '239kotoV-ultimate-secure'

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100))
    unique_code = db.Column(db.String(50))
    contact = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Ожидает')

with app.app_context():
    db.create_all()

# ТВОЙ SECRET KEY
TURNSTILE_SECRET = "0x4AAAAAACVwgqs7hUIqLYaoAqXKj8sA0mY"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buy/<item_name>', methods=['POST'])
def buy(item_name):
    token = request.form.get('cf-turnstile-response')
    verify = requests.post(
        "https://challenges.cloudflare.com/turnstile/v0/siteverify",
        data={'secret': TURNSTILE_SECRET, 'response': token}
    )
    if not verify.json().get('success'):
        return "<h1>Ошибка капчи! Роботам тут не место.</h1>", 403

    code = str(uuid.uuid4())[:8]
    new_order = Order(item=item_name, unique_code=code)
    db.session.add(new_order)
    db.session.commit()
    return redirect(url_for('payment', code=code))

@app.route('/payment/<code>', methods=['GET', 'POST'])
def payment(code):
    order = Order.query.filter_by(unique_code=code).first_or_404()
    if request.method == 'POST':
        order.contact = request.form.get('contact')
        order.status = 'Проверка тортов 🍰'
        db.session.commit()
        return f'''
        <body style="background:#050505; color:white; font-family:sans-serif; display:flex; align-items:center; justify-content:center; height:100vh; margin:0; text-align:center;">
            <div style="background:#111; padding:40px; border-radius:24px; border:1px solid #333; box-shadow:0 0 50px #00f0ff;">
                <h1 style="color:#00f0ff;">ЗАЯВКА ПРИНЯТА!</h1>
                <p style="color:#888;">Ожидай подтверждения от <b>@refiralov</b></p>
                <div style="margin:20px 0; color:#f0f; font-weight:bold;">СТАТУС: {order.status}</div>
                <a href="https://t.me/refiralov" style="display:inline-block; background:#fff; color:#000; padding:15px 30px; border-radius:12px; text-decoration:none; font-weight:bold;">НАПИСАТЬ АДМИНУ</a>
            </div>
        </body>
        '''
    return render_template('payment.html', order=order)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == '239kotoV':
            session['admin_logged_in'] = True
    if not session.get('admin_logged_in'):
        return render_template('admin.html', orders=[], logged_in=False)
    orders = Order.query.order_by(Order.id.desc()).all()
    return render_template('admin.html', orders=orders, logged_in=True)

@app.route('/admin/update_status/<int:id>/<new_status>')
def update_status(id, new_status):
    if not session.get('admin_logged_in'): return redirect('/admin')
    order = Order.query.get(id)
    if order:
        order.status = new_status
        db.session.commit()
    return redirect('/admin')

@app.route('/admin/delete/<int:id>')
def delete_order(id):
    if not session.get('admin_logged_in'): return redirect('/admin')
    order = Order.query.get(id)
    if order:
        db.session.delete(order)
        db.session.commit()
    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True)
    
