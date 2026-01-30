@app.route('/payment/<code>', methods=['GET', 'POST'])
def payment(code):
    order = Order.query.filter_by(unique_code=code).first_or_404()
    if request.method == 'POST':
        order.contact = request.form.get('contact')
        order.status = 'Проверка тортов 🍰'
        db.session.commit()
        
        # СТРАНИЦА УСПЕХА С КРУТЫМ ДИЗАЙНОМ
        return f'''
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ background: #050505; color: white; font-family: 'Courier New', monospace; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
                .success-card {{ background: #111; padding: 40px; border-radius: 24px; border: 1px solid #333; text-align: center; box-shadow: 0 0 50px rgba(0, 240, 255, 0.2); max-width: 400px; width: 90%; }}
                .icon {{ font-size: 50px; margin-bottom: 20px; filter: drop-shadow(0 0 10px #f0f); }}
                h1 {{ color: #00f0ff; text-transform: uppercase; letter-spacing: 2px; font-size: 1.5rem; }}
                p {{ color: #888; line-height: 1.6; margin: 20px 0; }}
                .status-label {{ background: #222; padding: 8px 15px; border-radius: 8px; color: #f0f; font-weight: bold; border: 1px solid #333; }}
                .tg-btn {{ display: inline-block; margin-top: 30px; background: #fff; color: #000; text-decoration: none; padding: 15px 30px; border-radius: 12px; font-weight: bold; transition: 0.3s; text-transform: uppercase; }}
                .tg-btn:hover {{ background: #00f0ff; transform: scale(1.05); box-shadow: 0 0 20px #00f0ff; }}
            </style>
        </head>
        <body>
            <div class="success-card">
                <div class="icon">⚡</div>
                <h1>Заявка принята!</h1>
                <p>Твой запрос на вступление в <b>TG BETA</b> отправлен модератору. Проверка NFT обычно занимает 15-30 минут.</p>
                <div style="margin: 25px 0;">
                    <span class="status-label">СТАТУС: {order.status}</span>
                </div>
                <a href="https://t.me/refiralov" class="tg-btn">Написать @refiralov</a>
            </div>
        </body>
        </html>
        '''
    return render_template('payment.html', order=order)
    
