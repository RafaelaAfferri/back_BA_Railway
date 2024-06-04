from flask_jwt_extended import jwt_required
from flask import Blueprint, request
from bson.objectid import ObjectId
from config import alunos
import datetime

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
