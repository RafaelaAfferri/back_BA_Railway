from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from bson.objectid import ObjectId
from config import casos, alunos
import datetime
from utils import generate_pdf
import os

casos_bp = Blueprint('casos', __name__)

# @casos_bp.route('/casos', methods=['POST'])
# @jwt_required()
# def register_caso():
#     try:
#         data = request.get_json()
#         aluno = alunos.find_one({"_id": ObjectId(data["aluno"])})
#         data["urgencia"] = data["urgencia"].upper()
#         data["status"] = data["status"].upper()
#         if not aluno:
#             return {"error": "Aluno não encontrado"}, 400
#         if data["ligacao"]:
#             data["ligacoes"] = [{"abae":data["abae"], "data":data["data"], "telefone":data["telefone"], "observacao":data["observacao"]}]
#         data["aluno"] = aluno
#         #cadastrar na base de dados
#         casos.insert_one(data)     
#         return {"message": "Caso registrado com sucesso"}, 201
#     except Exception as e:
#         return {"error": str(e)}, 500

#opacao de filtro por alunos
@casos_bp.route('/casos', methods=['GET'])
@jwt_required()
def get_casos():
    try:
        id_aluno = request.args.get('aluno_id')
        status = request.args.get('status')
        if id_aluno and status:
            data = casos.find_one({"aluno._id": ObjectId(id_aluno), "status": status})
            data['_id'] = str(data['_id'])
            data["aluno"]["_id"] = str(data["aluno"]["_id"])
            return jsonify({"caso": data}), 200
        if status:
            data = casos.find_one({"status": status})

            data['_id'] = str(data['_id'])
            data["aluno"]["_id"] = str(data["aluno"]["_id"])
            return jsonify({"caso": data}), 200
        if id_aluno:
            data = casos.find_one({"aluno._id": ObjectId(id_aluno)})
            data['_id'] = str(data['_id'])
            data["aluno"]["_id"] = str(data["aluno"]["_id"])
            return jsonify({"caso": data}), 200
        
        data = casos.find_one()
 
        data['_id'] = str(data['_id'])
        data["aluno"]["_id"] = str(data["aluno"]["_id"])
            
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
        aluno = alunos.find_one({"_id": ObjectId(caso["aluno"]["_id"])})
        if not aluno:
            return {"error": "Aluno não encontrado"}, 400
        data["aluno"] = aluno
        if "ligacao" in data and data["ligacao"]:
            caso["ligacoes"].append({"abae":data["abae"], "data":data["data"], "telefone":data["telefone"], "observacao":data["observacao"]})
        if "visita" in data and data["visita"]:
            caso["visitas"].append({"abae":data["abae"], "data":data["data"], "observacao":data["observacao"]})
        
        if "atendimento" in data and data["atendimento"]:
            caso["atendimentos"].append({"func":data["func"], "data":data["data"], "observacao":data["observacao"], "responsavel":data["responsavel"]})
        casos.update_one(filter_, {"$set": caso})
        return jsonify({"mensagem": "Caso atualizado com sucesso!"}), 200
    except Exception as e:
        return {"erro":str(e)}, 500
   

# @casos_bp.route('/casos/<string:id>', methods=['DELETE'])
# @jwt_required()
# def delete_caso(id):
#     try:
#         caso = casos.find_one({"_id": ObjectId(id)})
#         if caso:
#             casos.delete_one({"_id": ObjectId(id)})
#             return jsonify({"message": "Caso deletado com sucesso"}), 200
#         else:
#             return jsonify({"error": "Caso não encontrado"}), 404
#     except Exception as e:
#         return {"error": str(e)}, 500

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
            "ra": data["ra"],
            "usuario": data["usuario"],
            "data": datetime.date.today().strftime("%d-%m-%Y") ,
            "ligacoes": data["ligacoes"],
            "visitas": data["visitas"],
            "atendimentos" : data["atendimentos"],
        }
        print(context)

        output_pdf_path = os.path.abspath('relatorio.pdf')

        context["logo_path"] = os.path.abspath('template/logo.png')
        generate_pdf(context, output_pdf_path)

        return send_file(output_pdf_path, as_attachment=True, download_name='relatorio.pdf')
    except Exception as e:
        return jsonify({"error": str(e)}), 500
