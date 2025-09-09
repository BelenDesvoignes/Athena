from flask import Flask, jsonify

app = Flask(__name__)

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "No se encontro el recurso"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "El servidor sufrio un error interno"}), 500

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "No tiene autorizacion"}), 401