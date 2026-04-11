from flask import Flask, render_template, request, redirect, session, url_for
from functools import wraps
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'segredo123'

# CONFIG DO BANCO
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://joao:1A2b3c4d.@34.39.230.118:5432/diario_obra'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

import urllib.parse

senha = urllib.parse.quote_plus("1A2b3c4d.")

db = SQLAlchemy(app)

# MODEL
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)

# CRIAR TABELAS
with app.app_context():
    db.create_all()

# DECORATOR LOGIN
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return wrap

# ROTAS
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    user = Usuario.query.filter_by(username=username).first()

    if user and user.senha == password:
        session['user'] = user.username
        return redirect(url_for('dashboard'))
    else:
        return "Login inválido"

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

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
    app.run(host='0.0.0.0', port=5000)