from flask import Flask, render_template, request, redirect, session, url_for
from functools import wraps

app = Flask(__name__)
app.secret_key = 'segredo123'


# ROTA DE LOGIN (sem banco ainda)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return wrap



@app.route('/')
def home():
    return render_template('index.html')

#USUARIO PADRAO (admin & 123)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username == 'admin' and password == '123':
        session['user'] = username
        return redirect(url_for('dashboard'))
    else:
        return render_template('index.html')
    
@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('menu-inicial.html')


@app.route('/contratos')
@login_required
def contratos():
    return render_template('contratos.html')



@app.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)