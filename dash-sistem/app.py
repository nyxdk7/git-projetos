from flask import Flask, render_template, request, redirect, session, url_for
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import urllib.parse

app = Flask(__name__)
app.secret_key = 'segredo123'

senha = urllib.parse.quote_plus("1A2b3c4d.")

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://joao:{senha}@34.39.230.118:5432/diario_obra'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    nivel = db.Column(db.String(20), nullable=False, default='engenheiro')

with app.app_context():
    db.create_all()

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return wrap

def nivel_required(nivel_permitido):
    def decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if 'nivel' not in session or session['nivel'] != nivel_permitido:
                return "Acesso negado"
            return f(*args, **kwargs)
        return wrap
    return decorator

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    user = Usuario.query.filter_by(username=username).first()

    if user and check_password_hash(user.senha, password):
        session['user'] = user.username
        session['nivel'] = user.nivel
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
    session.pop('nivel', None)
    return redirect(url_for('home'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            return "Preencha todos os campos"

        usuario_existente = Usuario.query.filter_by(username=username).first()
        if usuario_existente:
            return "Usuário já existe"

        novo_usuario = Usuario(
            username=username,
            senha=generate_password_hash(password),
            nivel='engenheiro'
        )

        db.session.add(novo_usuario)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('cadastro.html')

@app.route('/admin')
@login_required
@nivel_required('admin')
def admin():
    return "Área do administrador"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)