from flask import Flask, request
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import pymongo
import certifi
import json
import os

string_mongo = "mongodb+srv://admin:admin@cluster0.dc2vjrc.mongodb.net/"
client_mongo = pymongo.MongoClient(string_mongo, tlsCAFile=certifi.where())

accounts = client_mongo.buscaAtiva.accounts
tokens = client_mongo.buscaAtiva.tokens

app = Flask("Back-End Busca Ativa Escolar")
CORS(app)

app.config['JWT_SECRET_KEY'] = 'busca-ativa-escolar'
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

@app.route('/usuarios', methods=['POST'])
def register():
    try:
        data = request.get_json()
        encrypted_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user = {
            "email": data["email"],
            "password": encrypted_password,
            "permissao": data["permissao"],
            "nome": data["nome"]
        }
        if accounts.find_one({"email": data["email"]}):
            return {"error": "Email already registered"}, 400   
        accounts.insert_one(user)
        return {"message": "User registered successfully"}, 201
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = accounts.find_one({'email': data["email"]})
        if user and bcrypt.check_password_hash(user['password'], data['password']):
            access_token = create_access_token(identity=str(user['_id']))
            tokens.insert_one({"email": data["email"], "token": access_token})
            return {"token": access_token}, 200
        else:
            return {"error": "Invalid email or password"}, 401
    except Exception as e:
        return {"error": str(e)}, 500
    
@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        data = request.get_json()
        token = data['token']
        user = tokens.find_one({"token": token})
        if user:
            tokens.delete_one({"token": token}) 
            return {"message": "Logout successfully"}, 200
        else:
            return {"error": "Invalid token"}, 401
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(debug=True,port = 8000)