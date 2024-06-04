from flask_jwt_extended import create_access_token, jwt_required
from flask import Blueprint, request
from config import accounts, tokens
from flask_bcrypt import Bcrypt

auth_bp = Blueprint('auth', __name__)

bcrypt = Bcrypt()

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = accounts.find_one({'email': data["email"]})
        if user and bcrypt.check_password_hash(user['password'], data['password']):
            access_token = create_access_token(identity=str(user['_id']))
            tokens.insert_one({"email": data["email"], "token": access_token, "permissao": user["permissao"]})
            return {"token": access_token}, 200
        else:
            return {"error": "Invalid email or password"}, 401
    except Exception as e:
        return {"error": str(e)}, 500

@auth_bp.route('/logout', methods=['POST'])
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

@auth_bp.route('/verificar-login', methods=['POST'])
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