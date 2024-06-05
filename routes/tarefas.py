from flask_jwt_extended import jwt_required
from flask import Blueprint, request
from bson.objectid import ObjectId
from config import alunos
import datetime

tarefas_bp = Blueprint('tarefas', __name__)

@tarefas_bp.route('/tarefas/<string:id_aluno>/<string:id_tarefa>', methods=['DELETE'])
@jwt_required()
def delete_tarefa(id_aluno, id_tarefa):
    try:
        aluno = alunos.find_one({"_id": ObjectId(id_aluno)})
        if not aluno:
            return {"error": "Aluno não encontrado"}, 400
        for tarefa in aluno["tarefas"]:
            if tarefa["_id"] == id_tarefa:
                aluno["tarefas"].remove(tarefa)
                alunos.update_one({"_id": ObjectId(id_aluno)}, {"$set": aluno})
                return {"message": "Tarefa deletada com sucesso"}, 200
        return {"error": "Tarefa não encontrada"}, 404
    except Exception as e:
        return {"error": str(e)}, 500

@tarefas_bp.route('/tarefas/<string:id>', methods=['POST'])
@jwt_required()
def register_tarefa(id):
    try:
        aluno = alunos.find_one({"_id": ObjectId(id)})
        if not aluno:
            return {"error": "Aluno não encontrado"}, 400
        data = request.get_json()
        data["_id"] = str(ObjectId())
        data["data"] = datetime.datetime.now()
        data["status"] = "Em andamento"
        aluno["tarefas"].append(data)
        alunos.update_one({"_id": ObjectId(id)}, {"$set": aluno})
        return {"message": "Tarefa registrada com sucesso"}, 201
    except Exception as e:
        return {"error": str(e)}, 500
