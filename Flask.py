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
@jwt_required()
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
    
@app.route('/usuarios/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    '''
    Função para deletar usuário
    '''
    try:
        user = accounts.find_one({"_id": ObjectId(user_id)})
        if user:
            accounts.delete_one({"_id": ObjectId(user_id)})
            return {"message": "User deleted successfully"}, 200
        else:
            return {"error": "User not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 500

    
@app.route('/usuarios', methods=['GET'])
@jwt_required()
def getUsers():
    '''
    Função para listar todos os usuários
    '''
    try:
        users_list = []
        for user in accounts.find():
            user['_id'] = str(user['_id'])
            users_list.append(user)
        return jsonify(users_list), 200
    except Exception as e:
        return {"error": str(e)}, 500
    
@app.route('/usuarios/<user_id>', methods=['PUT'])
@jwt_required()
def updateUser(user_id):
    '''
    Função para atualizar usuário
    '''
    try:
        data = request.get_json()
        user = accounts.find_one({"_id": ObjectId(user_id)})
        if data["email"] != user["email"] and accounts.find_one({"email": data["email"]}):
            return {"error": "Email already registered"}, 400
        if data["email"] != user["email"]:
            user["email"] = data["email"]
        if data["nome"] != user["nome"]:
            user["nome"] = data["nome"]
        if data["permissao"] != user["permissao"]:
            user["permissao"] = data["permissao"]
        accounts.update_one({"_id": ObjectId(user_id)}, {"$set": user})  
        return jsonify({"message": "User updated successfully"}), 200          
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
        # user = {
        #     "nome": data["nome"],
        #     "turma": data["turma"],
        #     "RA": data["RA"],
        #     "status": data["status"],
        #     "urgencia": data["urgencia"],
        #     "endereco": data["endereco"],
        #     "telefone": data["telefone"],
        #     "telefone2": data["telefone2"],
        #     "responsavel": data["responsavel"],
        #     "responsavel2": data["responsavel2"],
        # }
    
        if alunos.find_one({"RA": data["RA"]}):
            return {"error": "Este aluno já existe"}, 400
        alunos.insert_one(data)
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
            if not all(k in data for k in ("nome", "turma", "RA", "status", "urgencia", "endereco", "telefone", "responsavel")):
                alunos.update_one({"_id": ObjectId(id)}, {"$set": aluno})
            return jsonify({"message": "Aluno atualizado com sucesso"}), 200
        else:
            return jsonify({"error": "Aluno não encontrado"}), 404
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/alunoBuscaAtiva/ra/<string:ra>', methods=['GET'])
@jwt_required()
def getAlunoByRA(ra):
    '''
    Função para buscar aluno na busca ativa pelo RA
    '''
    try:
        aluno = alunos.find_one({"RA": ra, "status": "andamento"})
        if aluno:
            aluno['_id'] = str(aluno['_id'])  # Convertendo ObjectId para string para retornar no JSON
            return jsonify(aluno), 200
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
      
#------------------CASOS------------------#
@app.route('/casos', methods=['POST'])
@jwt_required()
def register_caso():
    try:
        data = request.get_json()
        data["data"] = datetime.datetime.now()
        aluno = alunos.find_one({"_id": ObjectId(data["aluno"])})
        if not aluno:
            return {"error": "Aluno não encontrado"}, 400
        if alunos.find_one({"aluno": aluno, "status": "andamento"}):
            return {"error": "Este aluno já tem um caso em andamento"}, 400
        data["aluno"] = aluno
        #cadastrar na base de dados
        casos.insert_one(data)     
        return {"message": "Caso registrado com sucesso"}, 201
    except Exception as e:
        return {"error": str(e)}, 500

#opacao de filtro por alunos
@app.route('/casos', methods=['GET'])
@jwt_required()
def get_casos():
    try:
        id_aluno = request.args.get('aluno_id')
        if id_aluno:
            data = list(casos.find({"aluno._id": ObjectId(id_aluno)}))
            for caso in data:
                caso['_id'] = str(caso['_id'])
                caso["aluno"]["_id"] = str(caso["aluno"]["_id"])
            return jsonify({"caso": data}), 200
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
    app.run(debug=True,port = 8000)