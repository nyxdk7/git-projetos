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

class Obra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    lote = db.Column(db.String(50), nullable=True)

    usuarios = db.relationship('Usuario', backref='obra', lazy=True)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    nivel = db.Column(db.String(20), nullable=False, default='engenheiro')
    obra_id = db.Column(db.Integer, db.ForeignKey('obra.id'), nullable=True)


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
        session['user_id'] = user.id
        session['nivel'] = user.nivel
        session['obra_id'] = user.obra_id
        return redirect(url_for('dashboard'))
    else:
        return "Login inválido"

@app.route('/dashboard')
@login_required
def dashboard():
    if session.get('nivel') == 'admin':
        obras = Obra.query.all()
        return render_template('dashboard.html', admin=True, obras=obras)

    obra = None
    if session.get('obra_id'):
        obra = db.session.get(Obra, session['obra_id'])

    return render_template('dashboard.html', admin=False, obra=obra)

@app.route('/contratos')
@login_required
def contratos():
    return render_template('contratos.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
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
    usuarios = Usuario.query.all()
    obras = Obra.query.all()
    return render_template('admin.html', usuarios=usuarios, obras=obras)


# 👇 COLOQUE AQUI
@app.route('/obra/nova', methods=['GET', 'POST'])
@login_required
@nivel_required('admin')
def nova_obra():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        lote = request.form.get('lote', '').strip()

        if not nome:
            return "Informe o nome da obra"

        obra = Obra(nome=nome, lote=lote)
        db.session.add(obra)
        db.session.commit()

        return "Obra cadastrada com sucesso"

    return render_template('nova_obra.html')

@app.route('/admin/vincular-obra/<int:user_id>', methods=['POST'])
@login_required
@nivel_required('admin')
def vincular_obra(user_id):
    usuario = Usuario.query.get_or_404(user_id)
    obra_id = request.form.get('obra_id')

    if obra_id == '':
        usuario.obra_id = None
    else:
        usuario.obra_id = int(obra_id)

    db.session.commit()
    return redirect(url_for('admin'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)