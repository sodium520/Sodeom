import os
from app import create_app, db
from config import Config

app = create_app()

with app.app_context():
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app.db')
    if not os.path.exists(db_path):
        db.create_all()
        print("Database created successfully.")

if __name__ == '__main__':
    app.run(debug=True)