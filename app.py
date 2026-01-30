from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import os

app = Flask(__name__)
# Секретный ключ для защиты сессий твоего браузера
app.config['SECRET_KEY'] = 'kotoV-super-secret-key-999'

# Настройка базы данных
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Твой зашифрованный пароль (239kotoV)
ADMIN_HASH = 'scrypt:32768:8:1$iY8U2m9YvW1GkE0h$71f654060805125950d603e87002012643a3f01968868846747b2909409893d98947f9e8011f00889c976939634e9e0466439169864276709664448749870425'

# Модель заказа в базе
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100))
    unique_code = db.Column(db.String(50))
    contact = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Ожидает')

# Автоматическое создание базы данных
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

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Защита от перебора пароля (5 попыток)
    if session.get('attempts', 0) >= 5:
        return "Доступ заблокирован: слишком много попыток.", 403

    if request.method == 'POST':
        password = request.form.get('password')
        if check_password_hash(ADMIN_HASH, password):
            session['admin_logged_in'] = True
            session['attempts'] = 0
        else:
            session['attempts'] = session.get('attempts', 0) + 1
            return "Неверный пароль!", 401
    
    if not session.get('admin_logged_in'):
        return render_template('admin.html', orders=[], logged_in=False)
    
    orders = Order.query.all()
    return render_template('admin.html', orders=orders, logged_in=True)

@app.route('/admin/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True)
