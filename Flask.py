from flask import Flask, request, jsonify
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
alunos = client_mongo.buscaAtiva.alunos

app = Flask("Back-End Busca Ativa Escolar")
CORS(app)

app.config['JWT_SECRET_KEY'] = 'busca-ativa-escolar'
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

@app.route('/usuarios-type', methods=['GET'])
def getUsuarios():
    try:
        data = request.get_json()
        token = data["token"]
        user_token = tokens.find_one({'token': token})
        user = accounts.find_one({"_id": ObjectId(user_token["email"])})
        permissao_user = user["permissao"]
        return jsonify({"permissao": permissao_user}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
    
@app.route('/verificar-login', methods=['POST'])
@jwt_required()
def verificar_login():
    try:
        data = request.get_json()
        token = data["token"]
        user = tokens.find_one({'token': token })
        if user:
            return {"message": "Usuário encontrado"}, 200
        else:
            return {"message": "Usuário não encontrado"}, 404
    except Exception as e:
        return {"mensagem": str(e)}, 500
    

@app.route('/alunoBuscaAtiva', methods=['POST'])
def registerAluno():
    try:
        data = request.get_json()
        user = {
            "nome": data["nome"],
            "turma": data["turma"],
            "RA": data["RA"],
            "status": data["status"],
            "urgencia": data["urgencia"],
            "endereco": data["endereco"],
            "telefone": data["telefone"],
            "telefone2": data["telefone2"],
            "responsavel": data["responsavel"],
            "responsavel2": data["responsavel2"],
        }
    
        if alunos.find_one({"RA": data["RA"], "status":"andamento"}):
            return {"error": "Este aluno tem uma busca ativa não finalizada"}, 400
        alunos.insert_one(user)
        return {"message": "User registered successfully"}, 201
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/alunoBuscaAtiva/<string:id>', methods=['GET'])
def getAluno(id):
    try:
        aluno = alunos.find_one({"_id": ObjectId(id), "status":"andamento"})
        if aluno:
            aluno['_id'] = str(aluno['_id'])  # Convertendo ObjectId para string para retornar no JSON
            return jsonify(aluno), 200
        else:
            return jsonify({"error": "Aluno não encontrado"}), 404
    except Exception as e:
        return {"error": str(e)}, 500
    
@app.route('/alunoBuscaAtiva/<string:id>', methods=['PUT'])
def updateAluno(id):
    try:
        data = request.get_json()
        aluno = alunos.find_one({"_id": ObjectId(id), "status":"andamento"})
        if aluno:
            if data.get("nome") != aluno["nome"]:
                aluno["nome"] = data["nome"]
            if data.get("turma") != aluno["turma"]:
                aluno["turma"] = data["turma"]
            if data.get("RA") != aluno["RA"]:
                aluno["RA"] = data["RA"]
            if data.get("status") != aluno["status"]:
                aluno["status"] = data["status"]
            if data.get("urgencia") != aluno["urgencia"]:
                aluno["urgencia"] = data["urgencia"]
            if data.get("endereco") != aluno["endereco"]:
                aluno["endereco"] = data["endereco"]
            if data.get("telefone") != aluno["telefone"]:
                aluno["telefone"] = data["telefone"]
            if data.get("telefone2") != aluno["telefone2"]:
                aluno["telefone2"] = data["telefone2"]
            if data.get("responsavel") != aluno["responsavel"]:
                aluno["responsavel"] = data["responsavel"]
            if data.get("responsavel2") != aluno["responsavel2"]:
                aluno["responsavel2"] = data["responsavel2"]
            alunos.update_one({"_id": ObjectId(id)}, {"$set": aluno})
            return jsonify({"message": "Aluno atualizado com sucesso"}), 200
        else:
            return jsonify({"error": "Aluno não encontrado"}), 404
    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    app.run(debug=True,port = 8000)