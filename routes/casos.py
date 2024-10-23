from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from bson.objectid import ObjectId
from config import casos, alunos
import datetime
from utils import generate_pdf
import os
import io
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font

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
            data = list(casos.find({"aluno._id": ObjectId(id_aluno), "status": status}))
            for caso in data:
                caso['_id'] = str(caso['_id'])
                caso["aluno"]["_id"] = str(caso["aluno"]["_id"])
            return jsonify({"caso": data}), 200
        if status:
            data = list(casos.find({"status": status}))
            for caso in data:
                caso['_id'] = str(caso['_id'])
                caso["aluno"]["_id"] = str(caso["aluno"]["_id"])
            return jsonify({"caso": data}), 200
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
        if "status" in data:
            caso["status"] = data["status"]
        if "urgencia" in data:
            caso["urgencia"] = data["urgencia"]
        
        casos.update_one(filter_, {"$set": caso})
        return jsonify({"mensagem": "Caso atualizado com sucesso!"}), 200
    except Exception as e:
        return {"erro":str(e)}, 500
   

@casos_bp.route('/casos/relatorio-geral', methods=['GET'])
@jwt_required()
def relatorio_geral():
    try:
        turma = request.args.get('turma')
        ano = request.args.get('ano')
        n_visita =0
        n_ligacao = 0
        n_atendimento = 0
        if turma:
            data = list(casos.find({"aluno.turma": turma}))
        else:
            data = list(casos.find())

        for caso in data:
            caso['_id'] = str(caso['_id'])
            caso["aluno"]["_id"] = str(caso["aluno"]["_id"])

        if ano:
            for caso in data:
                for visita in caso["visitas"]:
                    #fatia visita, comeca no ano
                    if visita["data"][:4] == ano:
                        n_visita += 1
                caso["n_visita"] = n_visita
                for ligacao in caso["ligacoes"]:
                    if ligacao["data"][:4] == ano:
                        n_ligacao += 1
                caso["n_ligacao"] = n_ligacao
                for atendimento in caso["atendimentos"]:
                    if atendimento["data"][:4] == ano:
                        n_atendimento += 1
                caso["n_atendimento"] = n_atendimento
        
        else:
            for caso in data:
                caso["n_visita"] = len(caso["visitas"])
                caso["n_ligacao"] = len(caso["ligacoes"])
                caso["n_atendimento"] = len(caso["atendimentos"])
        
        # Create Excel workbook
        wb = Workbook()
        ws = wb.active
        if turma and ano:
            ws.title = f"Relatório_Geral{turma}_{ano}"
        elif turma:
            ws.title = f"Relatório_Geral{turma}"
        elif ano:
            ws.title = f"Relatório_Geral{ano}"
        else:
            ws.title = "Relatório_Geral"
        
        # Define headers
        headers = [
            "Nome do Aluno",
            "Turma",
            "Número de Visitas",
            "Número de Ligações",
            "Número de Atendimentos",
            "Status do Caso",
            "Urgência do Caso",
            "Faltas"
        ]
        
        # Style for headers
        header_fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")
        header_font = Font(bold=True)
        
        # Write headers
        for col, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col, value=header)
            cell.fill = header_fill
            cell.font = header_font
        
        # Write data
        for row, caso in enumerate(data, 2):
            ws.cell(row=row, column=1, value=caso["aluno"]["nome"])
            ws.cell(row=row, column=2, value=caso["aluno"]["turma"])
            ws.cell(row=row, column=3, value=caso["n_visita"])
            ws.cell(row=row, column=4, value=caso["n_ligacao"])
            ws.cell(row=row, column=5, value=caso["n_atendimento"])
            ws.cell(row=row, column=6, value=caso["status"])
            ws.cell(row=row, column=7, value=caso["urgencia"])
            ws.cell(row=row, column=8, value=caso["faltas"])
        
        # Adjust column widths
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column].width = adjusted_width
        
        # Save to memory buffer
        excel_file = io.BytesIO()
        wb.save(excel_file)
        excel_file.seek(0)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if turma and ano:
            filename = f'relatorio_geral_{turma}_{ano}_{timestamp}.xlsx'
        elif turma:
            filename = f'relatorio_geral_{turma}_{timestamp}.xlsx'
        elif ano:
            filename = f'relatorio_geral_{ano}_{timestamp}.xlsx'
        else:
            filename = f'relatorio_geral_{timestamp}.xlsx'
        
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=filename
        )
        
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
            "ra": data["ra"],
            "usuario": data["usuario"],
            "data": datetime.date.today().strftime("%d-%m-%Y") ,
            "ligacoes": data["ligacoes"],
            "visitas": data["visitas"],
            "atendimentos" : data["atendimentos"],
        }

        output_pdf_path = os.path.abspath('relatorio.pdf')

        context["logo_path"] = os.path.abspath('template/logo.png')
        generate_pdf(context, output_pdf_path)

        return send_file(output_pdf_path, as_attachment=True, download_name='relatorio.pdf')
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
