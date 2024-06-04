from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from bson.objectid import ObjectId
from config import casos, alunos
import datetime
from utils import generate_pdf
import os

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


@casos_bp.route('/casos/gerar-relatorio', methods=['POST'])
@jwt_required()
def gerar_relatorio():
    try:
        data = request.get_json()

        context = {
            "dre": data["dre"],
            "unidade_escolar": data["unidade_escolar"],
            "endereco": data["endereco"],
            "contato": data["contato"],
            "turma": data["turma"],
            "estudante": data["estudante"],
            "rf": data["rf"],
            "usuario": data["usuario"],
            "data": data["data"],
            "data_ocorrencia": data["data_ocorrencia"],
            "tipo_ocorrencia": data["tipo_ocorrencia"],
            "titulo_ocorrencia": data["titulo_ocorrencia"],
            "descricao": data["descricao"],
            "ligacoes": data["ligacoes"],
            "visitas": data["visitas"],
        }

        output_pdf_path = os.path.abspath('relatorio.pdf')

        context["logo_path"] = os.path.abspath('template/logo.png')
        generate_pdf(context, output_pdf_path)

        return send_file(output_pdf_path, as_attachment=True, download_name='relatorio.pdf')
    except Exception as e:
        return jsonify({"error": str(e)}), 500
