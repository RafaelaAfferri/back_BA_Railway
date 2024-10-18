from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import pymongo
import certifi
from config import CONFIG

app = Flask(__name__)
CORS(app)




app.config.from_object(CONFIG)

bcrypt = Bcrypt(app)
jwt = JWTManager(app)

client_mongo = pymongo.MongoClient(CONFIG.MONGO_URI, tlsCAFile=certifi.where())

from routes.auth import auth_bp
from routes.usuarios import usuarios_bp
from routes.alunosBuscaAtiva import alunos_bp
from routes.casos import casos_bp
from routes.tarefas import tarefas_bp

app.register_blueprint(auth_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(alunos_bp)
app.register_blueprint(casos_bp)
app.register_blueprint(tarefas_bp)

if __name__ == "__main__":
    app.run(debug=True, port=8000)
