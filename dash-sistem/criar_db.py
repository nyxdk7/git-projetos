from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # testa conexão
        db.session.execute(text("SELECT 1"))
        print("✅ Conectado no banco!")

        # cria tabelas
        db.create_all()
        print("🔥 Tabelas criadas!")

    except Exception as e:
        print("❌ Erro:", e)