from flask import Flask, render_template, request, redirect, session
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '239kotoV-super-key'

# ТВОЙ ПАРОЛЬ
ADMIN_PASSWORD = '239kotoV'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buy/<item_name>', methods=['POST'])
def buy(item_name):
    # Временная заглушка без базы данных
    return redirect(f'/payment/test-code-123')

@app.route('/payment/<code>', methods=['GET', 'POST'])
def payment(code):
    if request.method == 'POST':
        return "<h3>Оплата принята! Ожидайте подтверждения от @refiralov</h3>"
    # Передаем пустой объект заказа, чтобы страница не падала
    return render_template('payment.html', order={'unique_code': code})

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
        else:
            return "Неверный пароль!", 401
    
    if not session.get('admin_logged_in'):
        return render_template('admin.html', orders=[], logged_in=False)
    
    # Пока показываем пустой список, чтобы не было ошибки 500
    return render_template('admin.html', orders=[], logged_in=True)

@app.route('/admin/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True)
