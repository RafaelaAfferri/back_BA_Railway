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


#SECTION - LOGIN E CADASTRO

@app.route('/usuarios-permissao', methods=['POST'])
@jwt_required()
def getUsuarios():
    '''
    Função para retornar o tipo de usuário - determina o que ele pode acessar
    '''
    try:
        data = request.get_json()
        token = data["token"]
        user_token = tokens.find_one({'token': token})
        email = user_token["email"]
        user = accounts.find_one({"email": email})
        permissao = user["permissao"]
        return jsonify({"permissao": permissao}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/usuarios', methods=['POST'])
def register():
    '''
    Função para registrar usuário (email, senha, permissão e nome)
    '''
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
    '''
    Função para realizar login de usuário
    '''
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
    '''
    Função para realizar logout de usuário
    '''
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
    '''
    Função para verificar se o usuário está logado
    '''
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
    
#!SECTION - LOGIN E CADASTRO


#SECTION - ALUNOS

@app.route('/alunoBuscaAtiva', methods=['POST'])
@jwt_required()
def registerAluno():
    '''
    Função para registrar aluno na busca ativa - novo caso
    '''
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
@jwt_required()
def getAluno(id):
    '''
    Função para buscar aluno na busca ativa
    '''
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
@jwt_required()
def updateAluno(id):
    '''
    Função para atualizar aluno na busca ativa
    '''
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


@app.route('/alunoBuscaAtiva/<string:id>', methods=['DELETE'])
@jwt_required()
def deleteAluno(id):
    '''
    Função para deletar aluno na busca ativa
    '''
    try:
        aluno = alunos.find_one({"_id": ObjectId(id), "status":"andamento"})
        if aluno:
            alunos.delete_one({"_id": ObjectId(id)})
            return jsonify({"message": "Aluno deletado com sucesso"}), 200
        else:
            return jsonify({"error": "Aluno não encontrado"}), 404
    except Exception as e:
        return {"error": str(e)}, 500
    

@app.route('/alunosBuscaAtiva', methods=['GET'])
@jwt_required()
def getAlunos():
    '''
    Função para listar todos os alunos
    Filtros: turma, nome, ano, RA, urgencia, status
    Ordenação: urgencia, status
    '''
    try:
        data = request.args
        filters = {}
        
        # filtros
        if "turma" in data:
            filters["turma"] = data.get("turma")
        if "nome" in data:
            filters["nome"] = data.get("nome")
        if "ano" in data:
            filters["ano"] = data.get("ano")
        if "RA" in data:
            filters["RA"] = data.get("RA")
        if "urgencia" in data:
            filters["urgencia"] = data.get("urgencia")
        if "status" in data:
            filters["status"] = data.get("status")
        
        # ordenação
        sort_criteria = []
        if "ordenarPor" in data:
            order_by = data.get("ordenarPor")
            if order_by == "urgencia":
                sort_criteria.append(("urgencia", 1))  # TODO: Lista de urgencias
            elif order_by == "status":
                sort_criteria.append(("status", 1)) # TODO: Lista de status
        
        alunos_list = []
        for aluno in alunos.find(filters).sort(sort_criteria):
            aluno['_id'] = str(aluno['_id'])
            alunos_list.append(aluno)
        
        return jsonify(alunos_list), 200
    except Exception as e:
        return {"error": str(e)}, 500
    
if __name__ == '__main__':
    app.run(debug=True, port=8000)