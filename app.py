from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import uuid

app = Flask(__name__)
# Добавили специальный конфиг для стабильности базы
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Order(db.Model):
    id = db.Model.Field(db.Integer, primary_key=True)
    item = db.Model.Field(db.String(100))
    unique_code = db.Model.Field(db.String(50))
    contact = db.Model.Field(db.String(100))
    status = db.Model.Field(db.String(20), default='Ожидает')

# ВАЖНО: Эта часть создает базу данных сама
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buy/<item_name>', methods=['POST'])
def buy(item_name):
    new_order = Order(item=item_name, unique_code=str(uuid.uuid4())[:8])
    db.session.add(new_order)
    db.session.commit()
    return redirect(f'/payment/{new_order.unique_code}')

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
    orders = Order.query.all()
    logged_in = False
    if request.method == 'POST':
        if request.form.get('password') == 'admin123':
            logged_in = True
    return render_template('admin.html', orders=orders, logged_in=logged_in)

if __name__ == '__main__':
    app.run(debug=True)
    
