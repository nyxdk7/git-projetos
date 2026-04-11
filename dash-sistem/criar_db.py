from app import app, db
from sqlalchemy import text

with app.app_context():
    result = db.session.execute(text("SELECT * FROM usuario;"))
    print("USUARIOS NO BANCO:", result.fetchall())