from flask import Blueprint, request, jsonify, send_file, make_response
from flask_jwt_extended import jwt_required
from bson.objectid import ObjectId
from config import casos, alunos
import datetime
from utils import generate_pdf, create_excel_report_with_charts
import os
import io
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.layout import Layout, ManualLayout
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.text import RichText 
import xlsxwriter


casos_bp = Blueprint('casos', __name__)


@casos_bp.route('/casos', methods=['POST'])
def get_casos():
    try:
        id_aluno = request.args.get('aluno_id')
        data = request.get_json()
        status = None
        ano = None
        turma = None
        if 'status' in data:
            status = data["status"]
        if 'ano' in data:
            ano = data["ano"]
        if 'turma' in data:
            turma = data["turma"]

        
        if turma or ano:
            query = {}
            
            if turma:
                if len(turma) == 1:
                    query["aluno.turma"] = {"$regex": f"^{turma}"}
                else:
                    query["aluno.turma"] = turma
            
            data = list(casos.find(query))
            for caso in data:
                caso['_id'] = str(caso['_id'])
                caso["aluno"]["_id"] = str(caso["aluno"]["_id"])

            if ano:
                # Filtrar os eventos no ano especificado
                filtered_data = []
                for caso in data:
                    # Filtrar visitas, ligacoes e atendimentos para o ano especificado
                    caso["visitas"] = [visita for visita in caso["visitas"] if int(visita["data"][:4]) in ano]
                    caso["ligacoes"] = [ligacao for ligacao in caso["ligacoes"] if int(ligacao["data"][:4]) in ano]
                    caso["atendimentos"] = [atendimento for atendimento in caso["atendimentos"] if int(atendimento["data"][:4]) in ano]
                    
                    # Adicionar caso somente se houver visitas, ligações ou atendimentos no ano
                    if caso["visitas"] or caso["ligacoes"] or caso["atendimentos"]:
                        filtered_data.append(caso)
                return jsonify({"caso": filtered_data}), 200

            return jsonify({"caso": data}), 200

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
        print(e)
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



@casos_bp.route('/casos/relatorio-geral', methods=['POST'])
@jwt_required()
def relatorio_geral():
    try:
        data = request.get_json()
        turma = data["turma"]
        anos = data["anos"]
        n_visita = 0
        n_ligacao = 0
        n_atendimento = 0
        n_status = {}
        n_urgen = {}
        query = {}
        if turma:
            if len(turma) == 1:
                query["aluno.turma"] = {"$regex": f"^{turma}"}
            else:
                query["aluno.turma"] = turma
        
        data = list(casos.find(query))
        
        for caso in data:
            caso['_id'] = str(caso['_id'])
            caso["aluno"]["_id"] = str(caso["aluno"]["_id"])

        if ano:
            for caso in data:
                for visita in caso["visitas"]:
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
                if caso["status"] in n_status:
                    n_status[caso["status"]] += 1
                else:
                    n_status[caso["status"]] = 1

                if caso["urgencia"] in n_urgen:
                    n_urgen[caso["urgencia"]] += 1
                else:
                    n_urgen[caso["urgencia"]] = 1
        else:
            for caso in data:
                caso["n_visita"] = len(caso["visitas"])
                caso["n_ligacao"] = len(caso["ligacoes"])
                caso["n_atendimento"] = len(caso["atendimentos"])
                if caso["status"] in n_status:
                    n_status[caso["status"]] += 1
                else:
                    n_status[caso["status"]] = 1

                if caso["urgencia"] in n_urgen:
                    n_urgen[caso["urgencia"]] += 1
                else:
                    n_urgen[caso["urgencia"]] = 1
                
                
        
        # Create Excel workbook in memory
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet("Relatório_Geral")
        
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

        # Write headers with formatting
        header_format = workbook.add_format({'bold': True, 'bg_color': '#CCE5FF'})
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        # Write data to cells
        for row, caso in enumerate(data, 1):
            worksheet.write(row, 0, caso["aluno"]["nome"])
            worksheet.write(row, 1, caso["aluno"]["turma"])
            worksheet.write(row, 2, caso["n_visita"])
            worksheet.write(row, 3, caso["n_ligacao"])
            worksheet.write(row, 4, caso["n_atendimento"])
            worksheet.write(row, 5, caso["status"])
            worksheet.write(row, 6, caso["urgencia"])
            worksheet.write(row, 7, caso["faltas"])

        worksheet.conditional_format('C2:C{}'.format(len(data) + 1), {
            'type': '3_color_scale',
            'min_color': "#AAFFAA",  # Light green for high values
            'mid_color': "#FFFFAA",  # Yellow for mid values
            'max_color': "#FFAAAA"   # Light red for low values
        })

        worksheet.conditional_format('D2:D{}'.format(len(data) + 1), {
            'type': '3_color_scale',
            'min_color': "#AAFFAA",  # Light green for high values
            'mid_color': "#FFFFAA",  # Yellow for mid values
            'max_color': "#FFAAAA"   # Light red for low values
        })

        worksheet.conditional_format('E2:E{}'.format(len(data) + 1), {
            'type': '3_color_scale',
            'min_color': "#AAFFAA",  # Light green for high values
            'mid_color': "#FFFFAA",  # Yellow for mid values
            'max_color': "#FFAAAA"   # Light red for low values
        })

        # Apply conditional formatting to the "Número de Visitas" column (C2:C...)
        worksheet.conditional_format('H2:H{}'.format(len(data) + 1), {
            'type': '3_color_scale',
            'min_color': "#AAFFAA",  # Light green for high values
            'mid_color': "#FFFFAA",  # Yellow for mid values
            'max_color': "#FFAAAA"   # Light red for low values
        })
        # Adjust column widths
        worksheet.set_column('A:A', 20)  # Nome do Aluno
        worksheet.set_column('B:B', 10)  # Turma
        worksheet.set_column('C:C', 18)  # Número de Visitas
        worksheet.set_column('D:D', 20)  # Número de Ligações
        worksheet.set_column('E:E', 22)  # Número de Atendimentos
        worksheet.set_column('F:F', 18)  # Status do Caso
        worksheet.set_column('G:G', 18)  # Urgência do Caso
        worksheet.set_column('H:H', 10)  # Faltas



#------------------------ Gráficos ------------------------
        # Create a new worksheet for charts
        graficos_alunos = workbook.add_worksheet("Gráficos Alunos")
        graficos_turma = workbook.add_worksheet("Gráficos Turma")
        grafico_s_u = workbook.add_worksheet("Gráfico Status e Urgência")

        

#------------------------ ALUNOS X VISITAS  ------------------------
        # Create a bar chart for Alunos x Visitas
        chart_visita = workbook.add_chart({'type': 'column'})
        # Data for chart_visita
        chart_visita.add_series({
            'name': 'Número de Visitas',
            'categories': f'=Relatório_Geral!$A$2:$A${len(data) + 1}',
            'values': f'=Relatório_Geral!$C$2:$C${len(data) + 1}'
        })
        chart_visita.set_title({'name': 'Alunos x Visitas'})
        chart_visita.set_x_axis({'name': 'Alunos'})
        chart_visita.set_y_axis({'name': 'Número de Visitas', 'major_unit': 1})
        
        
        
        chart_visita.set_size({'height': 300})
        
        chart_visita.set_legend({'position': 'none'})

        # Insert chart into chart worksheet
        graficos_alunos.insert_chart('A1', chart_visita)

#------------------------ ALUNOS X LIGAÇÕES  ------------------------
        # Create a bar chart for Alunos x Ligações
        chart_lig = workbook.add_chart({'type': 'column'})
        # Data for chart_lig
        chart_lig.add_series({
            'name': 'Número de Ligações',
            'categories': f'=Relatório_Geral!$A$2:$A${len(data) + 1}',
            'values': f'=Relatório_Geral!$D$2:$D${len(data) + 1}'
        })
        chart_lig.set_title({'name': 'Alunos x Ligações'})
        chart_lig.set_x_axis({'name': 'Alunos'})
        chart_lig.set_y_axis({'name': 'Número de Ligações', 'major_unit': 1})
        
        chart_lig.set_legend({'position': 'none'})

        chart_lig.set_size({'height': 300})
        
        # Insert chart into chart worksheet
        graficos_alunos.insert_chart('A20', chart_lig)


#------------------------ ALUNOS X ATENDIMENTOS  ------------------------

        # Create a bar chart for Alunos x Atendimentos
        chart_atend = workbook.add_chart({'type': 'column'})
        # Data for chart_atend
        chart_atend.add_series({
            'name': 'Número de Atendimentos',
            'categories': f'=Relatório_Geral!$A$2:$A${len(data) + 1}',
            'values': f'=Relatório_Geral!$E$2:$E${len(data) + 1}'
        })
        chart_atend.set_title({'name': 'Alunos x Atendimentos'})
        chart_atend.set_x_axis({'name': 'Alunos'})
        chart_atend.set_y_axis({'name': 'Número de Atendimentos', 'major_unit': 1})

        chart_atend.set_legend({'position': 'none'})

        chart_atend.set_size({'height': 300})

        # Insert chart into chart worksheet
        graficos_alunos.insert_chart('A40', chart_atend)


#------------------------ GRAFICO TURMA X LIG X VIS X ATEND------------------------

        # Create a bar chart for Turma x Lig x Vis x Atend
        chart_turma = workbook.add_chart({'type': 'column'})
        # Data for chart_turma
        chart_turma.add_series({
            'name': 'Número de Visitas',
            'categories': f'=Relatório_Geral!$B$2:$B${len(data) + 1}',
            'values': f'=Relatório_Geral!$C$2:$C${len(data) + 1}'
        })
        chart_turma.add_series({
            'name': 'Número de Ligações',
            'categories': f'=Relatório_Geral!$B$2:$B${len(data) + 1}',
            'values': f'=Relatório_Geral!$D$2:$D${len(data) + 1}'
        })
        chart_turma.add_series({
            'name': 'Número de Atendimentos',
            'categories': f'=Relatório_Geral!$B$2:$B${len(data) + 1}',
            'values': f'=Relatório_Geral!$E$2:$E${len(data) + 1}'
        })    

        

        chart_turma.set_title({'name': 'Ligações, visitas, atendimentos por turma'})

        chart_turma.set_x_axis({'name': 'Turma'})
        chart_turma.set_y_axis({'name': 'Quantidade', 'major_unit': 1})                 

        chart_turma.set_size({'height': 450})

        graficos_turma.insert_chart('A1', chart_turma)


#------------------------ GRAFICO FALTA X TURMA ------------------------
        chart_turma_falta = workbook.add_chart({'type': 'column'})
        # Data for chart_turma
        chart_turma_falta.add_series({
            'name': 'Faltas',
            'categories': f'=Relatório_Geral!$B$2:$B${len(data) + 1}',
            'values': f'=Relatório_Geral!$H$2:$H${len(data) + 1}'
        })

        chart_turma_falta.set_title({'name': 'Faltas por turma'})
        chart_turma_falta.set_x_axis({'name': 'Turma'})
        chart_turma_falta.set_y_axis({'name': 'Faltas', 'major_unit': 5, 'minor_unit': 1})
        chart_turma_falta.set_legend({'position': 'none'})

        chart_turma_falta.set_size({'height': 450})
        
        # Insert chart into chart worksheet
        graficos_turma.insert_chart('A30', chart_turma_falta)


#---------------------------------GRAFICO STATUS---------------------------------
        hidden_sheet = workbook.add_worksheet('HiddenData')
        hidden_sheet.hide()
        # Write the data in the hidden sheet
        row = 0
        for key, value in n_status.items():
            hidden_sheet.write(row, 0, key)  # Categories
            hidden_sheet.write(row, 1, value)  # Values
            row += 1

        # Create the doughnut chart
        chart_status = workbook.add_chart({'type': 'doughnut'})

        # Define ranges referring to the hidden sheet
        categories_range = f"HiddenData!$A$1:$A${len(n_status)}"
        values_range = f"HiddenData!$B$1:$B${len(n_status)}"

        # Now pass the ranges to the chart
        chart_status.add_series({
            'name': 'Status',
            'categories': categories_range,
            'values': values_range,
            'points': [
            {"fill": {"color": "#FBD542"}},
            {"fill": {"color": "#007bff"}},
            ],
            
            
        })
        chart_status.set_title({'name': 'Status dos casos'})
        chart_status.set_size({'height': 300, 'width': 300})
        chart_status.set_legend({'position': 'right'})
        chart_status.set_rotation(90)

        grafico_s_u.insert_chart('A1', chart_status)


#---------------------------------GRAFICO URGÊNCIA---------------------------------
        hidden_sheet = workbook.add_worksheet('HiddenData2')
        hidden_sheet.hide()
        # Write the data in the hidden sheet
        row = 0
        for key, value in n_urgen.items():
            hidden_sheet.write(row, 0, key)
            hidden_sheet.write(row, 1, value)
            row += 1
            
        # Create the doughnut chart
        chart_urgencia = workbook.add_chart({'type': 'doughnut'})

        # Define ranges referring to the hidden sheet
        categories_range = f"HiddenData2!$A$1:$A${len(n_urgen)}"
        values_range = f"HiddenData2!$B$1:$B${len(n_urgen)}"

        # Now pass the ranges to the chart
        chart_urgencia.add_series({
            'name': 'Urgência',
            'categories': categories_range,
            'values': values_range,
            'points': [
            {"fill": {"color": "#007bff"}},
            {"fill": {"color": "#008000"}},
            {"fill": {"color": "#FBD542"}},
            {"fill": {"color": "#05263E"}},
            ],
        })
        chart_urgencia.set_title({'name': 'Urgência dos casos'})
        chart_urgencia.set_size({'height': 300, 'width': 300})
        chart_urgencia.set_legend({'position': 'right'})
        chart_urgencia.set_rotation(135)

        grafico_s_u.insert_chart('F1', chart_urgencia)


        # Close workbook and prepare response
        workbook.close()
        output.seek(0)
        
        # Generate filename with timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        if turma and ano:
            filename = f'relatorio_geral_{turma}_{ano}_{timestamp}.xlsx'
        elif turma:
            filename = f'relatorio_geral_{turma}_{timestamp}.xlsx'
        elif ano:
            filename = f'relatorio_geral_{ano}_{timestamp}.xlsx'
        else:
            filename = f'relatorio_geral_{timestamp}.xlsx'

        # Create response with send_file
        response = make_response(
            send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=filename
            )
        )

        # Add headers to response
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'

        return response

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
            "tarefas": data["tarefas"]
        }

        output_pdf_path = os.path.abspath('relatorio.pdf')

        context["logo_path"] = os.path.abspath('template/logo.png')
        generate_pdf(context, output_pdf_path)

        return send_file(output_pdf_path, as_attachment=True, download_name='relatorio.pdf')
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
