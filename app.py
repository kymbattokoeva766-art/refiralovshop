from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import uuid
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '239kotoV-super-safe-key'

# Настройка базы данных
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Модель заказа
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100))
    unique_code = db.Column(db.String(50))
    contact = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Ожидает')

# Попытка создать базу при запуске (безопасно)
with app.app_context():
    try:
        db.create_all()
    except:
        pass

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buy/<item_name>', methods=['POST'])
def buy(item_name):
    try:
        code = str(uuid.uuid4())[:8]
        new_order = Order(item=item_name, unique_code=code)
        db.session.add(new_order)
        db.session.commit()
        return redirect(f'/payment/{code}')
    except:
        return "Ошибка создания заказа. Попробуйте позже."

@app.route('/payment/<code>', methods=['GET', 'POST'])
def payment(code):
    try:
        order = Order.query.filter_by(unique_code=code).first_or_404()
        if request.method == 'POST':
            order.contact = request.form.get('contact')
            order.status = 'Оплачено (проверка)'
            db.session.commit()
            return "<h3>Оплата принята! Ожидайте подтверждения от @refiralov</h3>"
        return render_template('payment.html', order=order)
    except:
        return "Заказ не найден или ошибка базы."

# --- АДМИНКА (ИСПРАВЛЕННАЯ) ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # 1. Проверка пароля (чистая логика, без базы)
    if request.method == 'POST':
        if request.form.get('password') == '239kotoV':
            session['admin_logged_in'] = True
        else:
            return "Неверный пароль!", 401
    
    # 2. Если не вошел - кидаем на форму входа
    if not session.get('admin_logged_in'):
        return render_template('admin.html', orders=[], logged_in=False)
    
    # 3. БЕЗОПАСНАЯ загрузка заказов
    # Если база сломана, мы просто показываем пустой список, А НЕ ОШИБКУ 500
    orders = []
    try:
        orders = Order.query.all()
    except Exception as e:
        print(f"Ошибка базы: {e}")
        orders = [] # Просто пустой список, чтобы сайт работал
        
    return render_template('admin.html', orders=orders, logged_in=True)

@app.route('/admin/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect('/admin')

# --- КНОПКА СПАСЕНИЯ (ЛЕЧЕНИЕ БАЗЫ) ---
@app.route('/fix-db')
def fix_db():
    try:
        # Удаляем старый файл базы, если он есть
        if os.path.exists(db_path):
            os.remove(db_path)
        # Создаем чистую базу
        with app.app_context():
            db.create_all()
        return "База данных успешно исправлена! Теперь идите в /admin"
    except Exception as e:
        return f"Ошибка исправления: {e}"

if __name__ == '__main__':
    app.run(debug=True)
