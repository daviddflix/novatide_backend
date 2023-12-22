# app/__init__.py

from flask import Flask
from app.routes.FA_Bot.fa_bot import fa_bp
from app.routes.OpenAI.openai import openai_bp

def create_app():
    app = Flask(__name__)
    app.name = 'FA Bot'

    app.register_blueprint(fa_bp)
    app.register_blueprint(openai_bp)

    return app