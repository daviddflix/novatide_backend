# run.py
from app import create_app
from flask_cors import CORS

app = create_app()
CORS(app)

if __name__ == '__main__':
    app.run(debug=True, threaded=True, use_reloader=True)

# new_secret_key = os.urandom(24).hex()
# app.secret_key = new_secret_key