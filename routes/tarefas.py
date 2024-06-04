from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
import pymongo
from bson.objectid import ObjectId
import datetime
from config import alunos

tarefas_bp = Blueprint('tarefas', __name__)

@tarefas_bp.route('/tarefas/<string:id>', methods=['POST'])
@jwt_required()
def register_tarefa(id):
    try:
        aluno = alunos.find_one({"_id": ObjectId(id)})
        if not aluno:
            return {"error": "Aluno não encontrado"}, 400
        data = request.get_json()
        data["data"] = datetime.datetime.now()
        aluno["tarefas"].append(data)
        alunos.update_one({"_id": ObjectId(id)}, {"$set": aluno})
        return {"message": "Tarefa registrada com sucesso"}, 201
    except Exception as e:
        return {"error": str(e)}, 500
