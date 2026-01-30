from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import uuid
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '239kotoV-ultimate-safe-key'

# База данных
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

@app.route('/buy/<item_name>', methods=['POST'])
def buy(item_name):
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
        
        # КРАСИВАЯ СТРАНИЦА УСПЕХА ВМЕСТО БЕЛОГО ЭКРАНА
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ background: #050505; color: white; font-family: sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
                .card {{ background: #111; padding: 40px; border-radius: 24px; border: 1px solid #333; text-align: center; box-shadow: 0 0 50px rgba(0, 240, 255, 0.2); max-width: 400px; width: 90%; }}
                h1 {{ color: #00f0ff; text-transform: uppercase; font-size: 1.5rem; margin-bottom: 20px; }}
                p {{ color: #888; line-height: 1.6; }}
                .status {{ display: inline-block; margin: 20px 0; padding: 8px 15px; background: #222; color: #f0f; border-radius: 8px; font-weight: bold; border: 1px solid #444; }}
                .btn {{ display: block; background: #fff; color: #000; text-decoration: none; padding: 15px; border-radius: 12px; font-weight: bold; margin-top: 25px; transition: 0.3s; }}
                .btn:hover {{ background: #00f0ff; box-shadow: 0 0 20px #00f0ff; transform: scale(1.03); }}
            </style>
        </head>
        <body>
            <div class="card">
                <div style="font-size: 50px; margin-bottom: 10px;">⚡</div>
                <h1>Заявка принята!</h1>
                <p>Твой запрос отправлен. Модератор проверит оплату в течение 15-30 минут.</p>
                <div class="status">СТАТУС: {order.status}</div>
                <a href="https://t.me/refiralov" class="btn">НАПИСАТЬ @REFIRALOV</a>
            </div>
        </body>
        </html>
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

@app.route('/admin/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True)
