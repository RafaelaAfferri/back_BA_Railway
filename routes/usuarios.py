from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config import accounts, tokens
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt
import os
import random
import string

usuarios_bp = Blueprint('usuarios', __name__)

bcrypt = Bcrypt()

@usuarios_bp.route('/port')
def check_port():
    return f'PORT: {os.getenv("PORT")}'


@usuarios_bp.route('/teste', methods=['GET'])
def test():
    return 'hello'

@usuarios_bp.route('/usuarios', methods=['POST'])
def register():
    try:
        data = request.get_json()
        senha = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        user = {
            "nomeusuario": data["nomeusuario"],
            "password": bcrypt.generate_password_hash(senha).decode('utf-8'),
            "permissao": data["permissao"].upper(),
            "nome": data["nome"].capitalize()
        }
        if accounts.find_one({"nomeusuario": data["nomeusuario"]}):
            return {"error": "Nome de ususario já existe"}, 400
        accounts.insert_one(user)
        return {"message": "Usuário resgistrado com sucesso", "senha" : senha}, 201
    except Exception as e:
        return {"error": str(e)}, 500

@usuarios_bp.route('/usuarios/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:
        user = accounts.find_one({"_id": ObjectId(user_id)})
        if user:
            accounts.delete_one({"_id": ObjectId(user_id)})
            return {"message": "Usuário deletado com sucesso"}, 200
        else:
            return {"error": "Usuario não encontrado"}, 404
    except Exception as e:
        return {"error": str(e)}, 500

@usuarios_bp.route('/usuarios', methods=['GET'])
@jwt_required()
def getUsers():
    try:
        users_list = []
        for user in accounts.find():
            user['_id'] = str(user['_id'])
            users_list.append(user)
        return jsonify(users_list), 200
    except Exception as e:
        return {"error": str(e)}, 500

@usuarios_bp.route('/usuarios/<user_id>', methods=['PUT'])
@jwt_required()
def updateUser(user_id):
    try:
        data = request.get_json()
        user = accounts.find_one({"_id": ObjectId(user_id)})

        if data["nomeusuario"] != user["nomeusuario"] and accounts.find_one({"nomeusuario": data["nomeusuario"]}):
            return {"error": "Nome de usuario ja existe"}, 400
        if data["nomeusuario"] != user["nomeusuario"]:
            user["nomeusuario"] = data["nomeusuario"]
        if data["nome"] != user["nome"]:
            user["nome"] = data["nome"]
        user["permissao"] = data["permissao"].upper()
        accounts.update_one({"_id": ObjectId(user_id)}, {"$set": user})
        return jsonify({"message": "User updated successfully"}), 200
    except Exception as e:
        return {"error": str(e)}, 500
    
@usuarios_bp.route('/usuarios/senha/<user_id>', methods=['PUT'])
@jwt_required()
def updateSenha(user_id):
    try:
        data = request.get_json()
        user = accounts.find_one({"_id": ObjectId(user_id)})
        user["password"] = bcrypt.generate_password_hash(data["password"]).decode('utf-8')
        accounts.update_one({"_id": ObjectId(user_id)}, {"$set": user})
        return jsonify({"message": "Senha atualizada com sucesso"}), 200
    except Exception as e:
        return {"error": str(e)}, 500

@usuarios_bp.route('/usuarios-permissao', methods=['POST'])
@jwt_required()
def getUsuarios():
    '''
    Função para retornar o tipo de usuário - determina o que ele pode acessar
    '''
    try:
        data = request.get_json()
        token = data["token"]
        user_token = tokens.find_one({'token': token})
        nomeusuario = user_token["nomeusuario"]
        user = accounts.find_one({"nomeusuario": nomeusuario})
        permissao = user["permissao"]
        return jsonify({"permissao": permissao}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @usuarios_bp.route('/usuarios-dados', methods=['POST'])
# @jwt_required()
# def getDadosUsuario():
#     '''
#     Função para retornar os dados do usuário
#     '''
#     try:
#         data = request.get_json()
#         token = data["token"]
#         user_token = tokens.find_one({'token': token})
#         nomeusuario = user_token["nomeusuario"]
#         user = accounts.find_one({"nomeusuario": nomeusuario})
#         user["_id"] = str(user["_id"])
#         return jsonify(user), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@usuarios_bp.route('/usuarios-dados', methods=['POST'])
@jwt_required()
def getDadosUsuario():
    try:
        data = request.get_json()
        token = data["token"]
        user_token = tokens.find_one({'token': token})
        if not user_token:
            raise ValueError("Token inválido ou não encontrado", token)
        nomeusuario = user_token["nomeusuario"]
        user = accounts.find_one({"nomeusuario": nomeusuario})
        if not user:
            raise ValueError("Usuário não encontrado")
        user["_id"] = str(user["_id"])
        return jsonify(user), 200
    except Exception as e:
        print(f"Erro no backend: {str(e)}")  # Log de erro detalhado
        return jsonify({"error": str(e)}), 500
