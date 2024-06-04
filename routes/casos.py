from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from bson.objectid import ObjectId
import datetime
from config import casos, alunos

casos_bp = Blueprint('casos', __name__)

@casos_bp.route('/casos', methods=['POST'])
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
        casos.insert_one(data)
        return {"message": "Caso registrado com sucesso"}, 201
    except Exception as e:
        return {"error": str(e)}, 500

@casos_bp.route('/casos', methods=['GET'])
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

@casos_bp.route('/casos/<string:id>', methods=['PUT'])
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
        return {"erro": str(e)}, 500

@casos_bp.route('/casos/<string:id>', methods=['DELETE'])
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
