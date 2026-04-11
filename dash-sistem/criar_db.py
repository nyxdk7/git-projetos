from app import app, db
from sqlalchemy import text

with app.app_context():
    result = db.session.execute(text("SELECT current_database();"))
    print("BANCO:", result.fetchone())