from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from bson.objectid import ObjectId
from config import alunos, casos

alunos_bp = Blueprint('alunos', __name__)

@alunos_bp.route('/alunoBuscaAtiva', methods=['POST'])
@jwt_required()
def registerAluno():
    try:
        data = request.get_json()
        if alunos.find_one({"RA": data["RA"]}):
            return {"error": "Este aluno já existe"}, 400
        data["nome"] = data["nome"].capitalize()
        data["turma"] = str(data["turma"][0]) + data["turma"][1].upper()
        data["tarefas"] = []
        alunos.insert_one(data)
        caso = {}
        caso["ligacoes"] = []
        caso["visitas"] = []
        caso["atendimentos"] = []
        caso["aluno"] = data
        caso["status"] = "EM ABERTO"
        caso["urgencia"] = "NÃO INFORMADO"
        #cadastrar na base de dados
        casos.insert_one(caso)     
        return {"message": "User registered successfully"}, 201
    except Exception as e:
        return {"error": str(e)}, 500

@alunos_bp.route('/alunoBuscaAtiva/<aluno_id>', methods=['PUT'])
@jwt_required()
def updateAluno(aluno_id):
    try:
        data = request.get_json()
        data["nome"] = data["nome"].capitalize()
        data["turma"] = str(data["turma"][0]) + data["turma"][1].upper()
        aluno = alunos.find_one({"_id": ObjectId(aluno_id)})
        if data["nome"] != aluno["nome"]:
            aluno["nome"] = data["nome"]
        if data["turma"] != aluno["turma"]:
            aluno["turma"] = data["turma"]
        if data["endereco"] != aluno["endereco"]:
            aluno["endereco"] = data["endereco"]
        if data["telefone"] != aluno["telefone"]:
            aluno["telefone"] = data["telefone"]
        if data["telefone2"] != aluno["telefone2"]:
            aluno["telefone2"] = data["telefone2"]
        if data["responsavel"] != aluno["responsavel"]:
            aluno["responsavel"] = data["responsavel"]
        if data["responsavel2"] != aluno["responsavel2"]:
            aluno["responsavel2"] = data["responsavel2"]
        alunos.update_one({"_id": ObjectId(aluno_id)}, {"$set": aluno})
        return jsonify({"message": "User updated successfully"}), 200
    except Exception as e:
        return {"error": str(e)}, 500

@alunos_bp.route('/alunoBuscaAtiva/ra/<string:ra>', methods=['GET'])
@jwt_required()
def getAlunoByRA(ra):
    try:
        aluno = alunos.find_one({"RA": ra, "status": "andamento"})
        if aluno:
            aluno['_id'] = str(aluno['_id'])
            return jsonify(aluno), 200
        else:
            return jsonify({"error": "Aluno não encontrado"}), 404
    except Exception as e:
        return {"error": str(e)}, 500

@alunos_bp.route('/alunoBuscaAtiva/<aluno_id>', methods=['DELETE'])
@jwt_required()
def delete_aluno(aluno_id):
    try:
        aluno = alunos.find_one({"_id": ObjectId(aluno_id)})
        if aluno:
            casos.delete_one({"aluno._id": ObjectId(aluno_id)})
            alunos.delete_one({"_id": ObjectId(aluno_id)})
            return {"message": "Aluno deleted successfully"}, 200
        else:
            return {"error": "Aluno not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 500

@alunos_bp.route('/alunoBuscaAtiva', methods=['GET'])
@jwt_required()
def getAlunos():
    try:
        alunos_list = []
        for alunos1 in alunos.find():
            alunos1['_id'] = str(alunos1['_id'])
            alunos_list.append(alunos1)
        return jsonify(alunos_list), 200
    except Exception as e:
        return {"error": str(e)}, 500

@alunos_bp.route('/alunoBuscaAtiva/<aluno_id>', methods=['GET'])
@jwt_required()
def getAlunosID(aluno_id):
    try:
        aluno = alunos.find_one({"_id": ObjectId(aluno_id)})
        if aluno:
            aluno['_id'] = str(aluno['_id'])
            return jsonify(aluno), 200
        else:
            return jsonify({"error": "Aluno não encontrado"}), 404
    except Exception as e:
        return {"error": str(e)}, 500
    


@alunos_bp.route('/alunoBuscaAtiva/caso/<caso_id>', methods=['GET'])
@jwt_required()
def getAlunosCasoId(caso_id):
    try:
        caso = casos.find_one({"_id": ObjectId(caso_id)})
        if caso:
            aluno = alunos.find_one({"_id": ObjectId(caso["aluno"]["_id"])})
            aluno['_id'] = str(aluno['_id'])
            return jsonify(aluno), 200
       
        else:
            return jsonify({"error": "Aluno não encontrado"}), 404
    except Exception as e:
        return {"error": str(e)}, 500