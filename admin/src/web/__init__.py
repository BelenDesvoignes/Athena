from flask import Flask, jsonify,render_template,abort

app = Flask(__name__)

def create_app(env="development", static_folder="../../static"):
    app = Flask(__name__, static_folder=static_folder)

    @app.route('/')
    def home():
        return render_template("home.html")
    
    

    @app.route('/not_found')
    @app.errorhandler(404)
    def not_found(error):
        return render_template("error_404.html"), 404
    #return jsonify({"error": "No se encontro el recurso"}), 404

    @app.route('/internal_error')
    def error_500():
        return abort(500)

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("error_500.html"), 500
    #return jsonify({"error": "El servidor sufrio un error interno"}), 500

    @app.route('/protected')
    def error_401():
        return abort(401)

    @app.errorhandler(401)
    def unauthorized(error):
        return render_template("error_401.html"), 401
    #return jsonify({"error": "No tiene autorizacion"}), 401






    return app
