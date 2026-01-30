from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import uuid
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '239kotoV-secret-key-final'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shop.db')
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

@app.route('/buy/<item_name>', methods=['POST'])
def buy(item_name):
    code = str(uuid.uuid4())[:8]
    new_order = Order(item=item_name, unique_code=code)
    db.session.add(new_order)
    db.session.commit()
    return redirect(f'/payment/{code}')

@app.route('/payment/<code>', methods=['GET', 'POST'])
def payment(code):
    order = Order.query.filter_by(unique_code=code).first_or_404()
    if request.method == 'POST':
        order.contact = request.form.get('contact')
        order.status = 'Оплачено (проверка)'
        db.session.commit()
        return "<h3>Оплата принята! Ожидайте подтверждения от @refiralov</h3>"
    return render_template('payment.html', order=order)

# ИСПРАВЛЕННЫЙ БЛОК АДМИНКИ ЗДЕСЬ
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        input_pass = request.form.get('password')
        if input_pass == '239kotoV':
            session['admin_logged_in'] = True
        else:
            return "Неверный пароль!", 401
    
    if not session.get('admin_logged_in'):
        return render_template('admin.html', orders=[], logged_in=False)
    
    try:
        orders = Order.query.all()
    except:
        orders = []
        
    return render_template('admin.html', orders=orders, logged_in=True)

@app.route('/admin/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True)
