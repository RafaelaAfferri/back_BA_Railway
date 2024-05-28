from flask import Flask, request, jsonify
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import pymongo
import certifi
import json
import os
import datetime

string_mongo = "mongodb+srv://admin:admin@cluster0.dc2vjrc.mongodb.net/buscaAtiva?retryWrites=true&w=majority"
client_mongo = pymongo.MongoClient(string_mongo, tlsCAFile=certifi.where())

accounts = client_mongo.buscaAtiva.accounts
tokens = client_mongo.buscaAtiva.tokens
alunos = client_mongo.buscaAtiva.alunos
casos = client_mongo.buscaAtiva.casos

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
    

#------------------ALUNOS------------------

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
            if not all(k in data for k in ("nome", "turma", "RA", "status", "urgencia", "endereco", "telefone", "responsavel")):
                alunos.update_one({"_id": ObjectId(id)}, {"$set": aluno})
            return jsonify({"message": "Aluno atualizado com sucesso"}), 200
        else:
            return jsonify({"error": "Aluno não encontrado"}), 404
    except Exception as e:
        return {"error": str(e)}, 500


#------------------CASOS------------------
@app.route('/casos', methods=['POST'])
@jwt_required()
def register_caso():
    try:
        data = request.get_json()
        data["data"] = datetime.datetime.now()
        aluno = alunos.find_one({"_id": ObjectId(data["aluno"])})
        if not aluno:
            return {"error": "Aluno não encontrado"}, 400
        data["aluno"] = aluno
        #cadastrar na base de dados
        casos.insert_one(data)     
        return {"message": "Caso registrado com sucesso"}, 201
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/casos', methods=['GET'])
@jwt_required()
def get_casos():
    try:
        data = list(casos.find())
        for caso in data:
            caso['_id'] = str(caso['_id'])
            caso["aluno"]["_id"] = str(caso["aluno"]["_id"])
        return jsonify({"caso": data}), 200
    except Exception as e:
        return {"error": str(e)}, 500
    
@app.route('/casos/<string:id>', methods=['PUT'])
@jwt_required()
def update_caso(id):
    try:
        filter_ = {"_id": ObjectId(id)}
        projection_ = {}
        caso = casos.find_one(filter_, projection_)
        if not caso:
            return jsonify({"erro": "Caso não encontrado!"}), 404
        data = request.get_json()
        aluno = alunos.find_one({"_id": ObjectId(data["aluno"])})
        if not aluno:
            return {"error": "Aluno não encontrado"}, 400
        data["aluno"] = aluno
        casos.update_one(filter_, {"$set": data})
        return jsonify({"mensagem": "Caso atualizado com sucesso!"}), 200
    except Exception as e:
        return {"erro":str(e)}, 500
    
@app.route('/casos/<string:id>', methods=['DELETE'])
@jwt_required()
def delete_caso(id):
    try:
        caso = casos.find_one({"_id": ObjectId(id)})
        if caso:
            casos.delete_one({"_id": ObjectId(id)})
            return jsonify({"message": "Caso deletado com sucesso"}), 200
        else:
            return jsonify({"error": "Caso não encontrado"}), 404
    except Exception as e:
        return {"error": str(e)}, 500



if __name__ == "__main__":
    app.run(debug=True,port = 5500)