# run.py
import os
from app import create_app
from flask_cors import CORS
from config import User, Session
from flask_login import LoginManager

app = create_app()
CORS(app)

new_secret_key = os.urandom(24).hex()
app.secret_key = new_secret_key

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # Load user from the database using user_id
    with Session() as session:
        return session.query(User).get((int(user_id)))


if __name__ == '__main__':
    app.run(debug=True, threaded=True, use_reloader=False)