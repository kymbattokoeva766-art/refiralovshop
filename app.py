from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import uuid
import os
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'math-captcha-239'

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/captcha/<item_name>', methods=['GET', 'POST'])
def captcha(item_name):
    if request.method == 'POST':
        user_answer = request.form.get('answer')
        correct_answer = session.get('captcha_answer')
        
        if user_answer and int(user_answer) == correct_answer:
            # Если ответ верный, создаем заказ
            code = str(uuid.uuid4())[:8]
            new_order = Order(item=item_name, unique_code=code)
            db.session.add(new_order)
            db.session.commit()
            return redirect(url_for('payment', code=code))
        else:
            return redirect(url_for('captcha', item_name=item_name, error=1))

    # Генерируем новый пример
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    session['captcha_answer'] = num1 + num2
    return render_template('captcha.html', n1=num1, n2=num2, item=item_name)

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
                <p style="color:#888;">Ожидайте подтверждения от <b>@refiralov</b></p>
                <div style="margin:20px 0; color:#f0f; font-weight:bold; border:1px solid #444; padding:10px; border-radius:10px;">СТАТУС: {order.status}</div>
                <a href="https://t.me/refiralov" style="display:inline-block; background:#fff; color:#000; padding:15px 30px; border-radius:12px; text-decoration:none; font-weight:bold;">СВЯЗАТЬСЯ С АДМИНУ</a>
            </div>
        </body>
        '''
    return render_template('payment.html', order=order)

# Админка остается прежней
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == '239kotoV':
            session['admin_logged_in'] = True
    if not session.get('admin_logged_in'):
        return render_template('admin.html', orders=[], logged_in=False)
    orders = Order.query.order_by(Order.id.desc()).all()
    return render_template('admin.html', orders=orders, logged_in=True)

if __name__ == '__main__':
    app.run(debug=True)
