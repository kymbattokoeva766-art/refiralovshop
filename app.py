from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import uuid
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'neon-admin-2026'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100))
    unique_code = db.Column(db.String(50), unique=True)
    contact = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Ожидание')
    date = db.Column(db.DateTime, default=db.func.current_timestamp())

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/captcha/<item_name>', methods=['GET', 'POST'])
def captcha(item_name):
    import random
    if request.method == 'POST':
        if int(request.form.get('answer')) == session.get('captcha_ans'):
            code = str(uuid.uuid4())[:8].upper()
            new_order = Order(item=item_name, unique_code=code)
            db.session.add(new_order)
            db.session.commit()
            return redirect(url_for('user_cabinet', code=code))
        return redirect(url_for('captcha', item_name=item_name, error=1))
    n1, n2 = random.randint(1, 10), random.randint(1, 10)
    session['captcha_ans'] = n1 + n2
    return render_template('captcha.html', n1=n1, n2=n2)

@app.route('/cabinet/<code>', methods=['GET', 'POST'])
def user_cabinet(code):
    order = Order.query.filter_by(unique_code=code).first_or_404()
    if request.method == 'POST':
        order.contact = request.form.get('contact')
        order.status = 'Проверка'
        db.session.commit()
    return render_template('cabinet.html', order=order)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('pass') == '239kotoV':
            session['admin'] = True
    if not session.get('admin'):
        return render_template('admin_login.html')
    orders = Order.query.order_by(Order.id.desc()).all()
    stats = {
        'total': Order.query.count(),
        'pending': Order.query.filter_by(status='Проверка').count()
    }
    return render_template('admin_panel.html', orders=orders, stats=stats)

@app.route('/admin/status/<int:id>/<status>')
def update_status(id, status):
    if session.get('admin'):
        order = Order.query.get(id)
        order.status = status
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/delete/<int:id>')
def delete_order(id):
    if session.get('admin'):
        order = Order.query.get(id)
        db.session.delete(order)
        db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
