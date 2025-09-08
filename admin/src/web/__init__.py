from flask import Flask, render_template

def create_app(env="development", static_folder=""):
    app = Flask(__name__, static_folder=static_folder)

    @app.route('/')
    def home():
        return render_template("home.html")
    
    return app