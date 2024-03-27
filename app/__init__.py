# app/__init__.py

from flask import Flask
from app.routes.multi_bot.multi_bot import multi_bot_bp
from app.routes.ask_ai.ask_ai import ai_bp
from app.routes.watchlist.watchlist import watchlist_bp

def create_app():
    app = Flask(__name__)
    app.name = 'AI Alpha Bots'

    app.register_blueprint(multi_bot_bp)
    app.register_blueprint(watchlist_bp)
    app.register_blueprint(ai_bp)

    return app