from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from config import accounts, tokens
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt

usuarios_bp = Blueprint('usuarios', __name__)

bcrypt = Bcrypt()

@usuarios_bp.route('/usuarios', methods=['POST'])
@jwt_required()
def register():
    try:
        data = request.get_json()
        encrypted_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        user = {
            "email": data["email"],
            "password": encrypted_password,
            "permissao": data["permissao"].upper(),
            "nome": data["nome"].capitalize()
        }
        if accounts.find_one({"email": data["email"]}):
            return {"error": "Email already registered"}, 400
        accounts.insert_one(user)
        return {"message": "User registered successfully"}, 201
    except Exception as e:
        return {"error": str(e)}, 500

@usuarios_bp.route('/usuarios/<user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    try:
        user = accounts.find_one({"_id": ObjectId(user_id)})
        if user:
            accounts.delete_one({"_id": ObjectId(user_id)})
            return {"message": "User deleted successfully"}, 200
        else:
            return {"error": "User not found"}, 404
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
        email = user_token["email"]
        user = accounts.find_one({"email": email})
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
#         email = user_token["email"]
#         user = accounts.find_one({"email": email})
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
        email = user_token["email"]
        user = accounts.find_one({"email": email})
        if not user:
            raise ValueError("Usuário não encontrado")
        user["_id"] = str(user["_id"])
        return jsonify(user), 200
    except Exception as e:
        print(f"Erro no backend: {str(e)}")  # Log de erro detalhado
        return jsonify({"error": str(e)}), 500
