from flask import Blueprint, request, jsonify, send_file, make_response
from flask_jwt_extended import jwt_required
from bson.objectid import ObjectId
from config import alunos, casos
import datetime
import pytz
import pandas as pd
import io
import xlsxwriter

alunos_bp = Blueprint('alunos', __name__)

import pandas as pd
import io

def tratar_arquivo_excel(file_storage):
    filename = file_storage.filename.lower()

    # Se for .xlsx, carrega normal
    if filename.endswith('.xlsx'):
        df = pd.read_excel(file_storage, engine='openpyxl')
        return df

    # Se for .xls, precisamos verificar se é fake HTML
    file_content = file_storage.read()
    file_storage.seek(0)  # Volta o ponteiro para permitir nova leitura

    if file_content[:100].lower().startswith((b'<html', b'<table', b'<!doc')):
        # É um fake HTML
        tabelas = pd.read_html(io.BytesIO(file_content))
        df_unificado = pd.concat(tabelas, ignore_index=True)
        return df_unificado
    else:
        # XLS legítimo, carrega normalmente
        df = pd.read_excel(file_storage, engine='xlrd')
        return df

def limpar_dataframe(df):
    # Se a primeira linha for toda NaN, remove
    if df.iloc[0].isnull().all():
        df = df.iloc[1:].reset_index(drop=True)

    # Agora, pega a primeira linha como header
    df.columns = df.iloc[0]
    df = df[1:].reset_index(drop=True)

    return df


@alunos_bp.route('/alunoBuscaAtiva', methods=['POST'])
@jwt_required()
def registerAluno():
    try:
        # data = request.get_json()
        if 'files' not in request.files:
            return {"error": "Nenhum arquivo foi enviado"}, 400
        files = request.files.getlist('files')  # Obtém a lista de arquivos enviados
        dict_turmas = {}
        
        for file in files:
            filename = file.filename.lower()
            
            
            try:
                df = tratar_arquivo_excel(file)
            except Exception as e:
                return {"error": f"Erro ao processar arquivo {file.filename}: {str(e)}"}, 400
            

            df = df.reset_index(drop=True)
            # Procurar a palavra "Turma"
            posicoes = df.isin(["Turma"]).values.nonzero()
            
            # Agora carregamos o arquivo com o engine correto
           
            #endereço, telefone, telefone2, responsavel2, faltas
            posicoes = df.isin(["Turma"]).values.nonzero()
            if len(posicoes[0]) == 0 or len(posicoes[1]) == 0:
                return {"error": "Palavra 'Turma' não encontrada na planilha"}, 400
            row = posicoes[0][0]
            col = posicoes[1][0]

            posicoes2 = df.isin(["Descrição"]).values.nonzero()
            if len(posicoes2[0]) == 0 or len(posicoes2[1]) == 0:
                return {"error": "Palavra 'Descrição' não encontrada na planilha"}, 400
            row2 = posicoes2[0][0]
            col2 = posicoes2[1][0]

            desc_val = df.iat[row2, col2 + 1] if (col2 + 1) < df.shape[1] else ""
            if "EJA" in desc_val:
                desc_info = " - EJA"
            else:
                desc_info = ""

            turma_val = df.iat[row, col + 1] if (col + 1) < df.shape[1] else ""
            turma_info = turma_val.split(" ") if turma_val else []
            if len(turma_info) < 3:
                return {"error": "Formato inesperado na célula da turma"}, 400
            turma_info = turma_info[2] + desc_info
            
            if turma_info in dict_turmas:
                return {"error": f"Turma {turma_info} está duplicada na planilha"}, 400
            dict_turmas[turma_info]=df

        dict_turmas_sorted = dict(sorted(dict_turmas.items(), reverse=True))

        # Agrupamento de turmas
        dfs_agrupados = {}
        for turma, df in dict_turmas_sorted.items():
            df_novo = df.iloc[3:].reset_index(drop=True)
            df_novo = limpar_dataframe(df_novo)


            numero_turma = turma[0]  # Pega o primeiro caractere da turma
            if numero_turma not in dfs_agrupados:
                dfs_agrupados[numero_turma] = []
            # Adiciona uma coluna indicando a turma original
            df_novo['turma'] = turma
            dfs_agrupados[numero_turma].append(df_novo)
        dfs_finais = {}
        for numero, lista_dfs in dfs_agrupados.items():
            dfs_finais[numero] = pd.concat(lista_dfs, ignore_index=True)
        
        formados=[]

        for key in dfs_finais:
            df = dfs_finais[key]
            required_columns = ["Nome do Aluno", "RA Prodesp", "Filiação 1", "turma", "Utiliz. T.E.G.", "Data Nascimento", "Situação Aluno"]
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                return {"error": f"Colunas ausentes na planilha: {', '.join(missing_columns)}"}, 400

            nomes = df["Nome do Aluno"].fillna("Vazio").tolist()
            ras = df["RA Prodesp"].fillna("Vazio").tolist()
            responsaveis1 = df["Filiação 1"].fillna("").tolist()
            turmas = df["turma"].fillna("Vazio").tolist()
            tegs = df["Utiliz. T.E.G."].fillna("NÃO").tolist()
            df["Data Nascimento"] = df["Data Nascimento"].fillna("").infer_objects(copy=False)
            datas = df["Data Nascimento"].tolist()
            situacoes = df["Situação Aluno"].tolist()

               
            alunos_list = alunos.find({"turma": { "$regex": f"^{key}", "$options": "i" }})
            #deleta alunos que não existem mais
            
            for aluno in alunos_list:
                if aluno["RA"] not in ras:
                    alunos.find_one({"_id": ObjectId(aluno["_id"])})
                    if aluno["turma"][0] == "9":
                        formados.append(aluno["RA"])
                        
                    elif int(aluno["atualizacao"]) - int(datetime.datetime.now().year) > 1:
                        casos.delete_one({"aluno._id": ObjectId(aluno["_id"])})
                        alunos.delete_one({"_id": ObjectId(aluno["_id"])})
                    elif aluno["ativo"] == "sim":
                        aluno["ativo"] = "nao"
                        aluno["atualizacao"] = datetime.datetime.now().year



            for i in range(len(nomes)):
                if tegs[i] == "UTILIZANDO":
                    tegs[i] = "SIM"
                if situacoes[i] == "VÍNCULO INDEVIDO":
                    continue
                if alunos.find_one({"RA": ras[i]}) and ras[i] != "Vazio":
                    data =  alunos.find_one({"RA": ras[i]})
                    
                    data["nome"] = nomes[i]
                    data["turma"] = turmas[i]
                    data["responsavel"] = responsaveis1[i]
                    data['faltas'] = 0
                    data["utiliz_teg"] = tegs[i]
                    data["dataNascimento"] = datas[i]
                    alunos.update_one({"RA": ras[i]}, {"$set": data})
                    continue
                data = {}
                if (ras[i]== "Vazio") or (nomes[i] == "Vazio") or (turmas[i] == "Vazio"):
                    data["situacao"] = "INCOMPLETO"
                else:
                    data["situacao"] = "COMPLETO"
                data["nome"] = nomes[i]
                data["RA"] = ras[i]
                data["turma"] = turmas[i]
                data["dataNascimento"] = datas[i]
                data["tarefas"] = []
                data["endereco"] = ''
                data["telefone"] = ''
                data["telefone2"] = ''
                data["responsavel"] = responsaveis1[i]
                data["responsavel2"] = ''
                data["faltas"] = 0
                data["utiliz_teg"] = tegs[i]
                data["atualizacao"] = datetime.datetime.now().year
                data["ativo"] = "sim"
                alunos.insert_one(data)
                caso = {}
                caso["ligacoes"] = []
                caso["visitas"] = []
                caso["atendimentos"] = []
                caso["aluno"] = data
                caso["status"] = "FINALIZADO"
                caso["faltas"] = int(data["faltas"])
                caso["urgencia"] = "INDEFINIDA"
                casos.insert_one(caso)
        turmas_existentes = alunos.distinct("turma")
        for turma in turmas_existentes:
            if turma not in dict_turmas:
                alunos_list = alunos.find({"turma": turma})
                for aluno in alunos_list:
                    if aluno["turma"][0] == "9":
                        formados.append(aluno["RA"])
                    elif int(aluno["atualizacao"]) - int(datetime.datetime.now().year) > 1:
                        casos.delete_one({"aluno._id": ObjectId(aluno["_id"])})
                        alunos.delete_one({"_id": ObjectId(aluno["_id"])})
                    elif aluno["ativo"] == "sim":
                        aluno["ativo"] = "nao"
                        aluno["atualizacao"] = datetime.datetime.now().year
        if len(formados) > 0:
            print(formados)
            print("entrou")
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet("Alunos_Formados")
            worksheet.write("A1", "RA")
            worksheet.write("B1", "Nome")
            worksheet.write("C1", "Turma")
            worksheet.write("D1", "Responsável")
            worksheet.write("F1", "dataNascimento")
            worksheet.write("G1", "Ano de Formatura")
            for i in range(len(formados)):
                aluno = alunos.find_one({"RA": formados[i]})
                worksheet.write(f"A{i+2}", formados[i])
                worksheet.write(f"B{i+2}", aluno["nome"])
                worksheet.write(f"C{i+2}", aluno["turma"])
                worksheet.write(f"D{i+2}", aluno["responsavel"])
                worksheet.write(f"E{i+2}", aluno["endereco"])
                worksheet.write(f"F{i+2}", aluno["dataNascimento"])
                worksheet.write(f"G{i+2}", datetime.datetime.now().year)
            
            worksheet2 = workbook.add_worksheet("Casos_Alunos")
            worksheet2.write("A1", "RA")
            worksheet2.write("B1", "Nome")
            worksheet2.write("C1", "Ligações")
            worksheet2.write("D1", "Visitas")
            worksheet2.write("E1", "Atendimentos")

            for i in range(len(formados)):
                aluno = alunos.find_one({"RA": formados[i]})
                caso = casos.find_one({"aluno.RA": formados[i]})
                worksheet2.write(f"A{i+2}", formados[i])
                worksheet2.write(f"B{i+2}", aluno["nome"])
                worksheet2.write(f"C{i+2}", len(caso["ligacoes"]))
                worksheet2.write(f"D{i+2}", len(caso["visitas"]))
                worksheet2.write(f"E{i+2}", len(caso["atendimentos"]))
                casos.delete_one({"aluno._id": ObjectId(aluno["_id"])})
                alunos.delete_one({"_id": ObjectId(aluno["_id"])})

            workbook.close()
            output.seek(0)

            filename = f"Alunos_Formados_{datetime.datetime.now().year}.xlsx"

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

        return {"message": "Alunos registrados com sucesso"}, 201
    except Exception as e:
        print(str(e))
        return {"error": str(e)}, 500


@alunos_bp.route('/alunoBuscaAtivaOne', methods=['POST'])
@jwt_required()
def registerAlunoOne(): 
    try:
        data = request.get_json()
        if alunos.find_one({"RA": data["RA"]}):
            return {"error": "Este aluno já existe"}, 400
        data["nome"] = data["nome"].capitalize()
        data["turma"] = str(data["turma"][0]) + data["turma"][1].upper()
        data["dataNascimento"] = data["dataNascimento"]
        data["tarefas"] = []
        data["situacao"] = "COMPLETO"
        data["ativo"] = "sim"
        data["atualizacao"] = datetime.datetime.now().year
        alunos.insert_one(data)
        caso = {}
        caso["ligacoes"] = []
        caso["visitas"] = []
        caso["atendimentos"] = []
        caso["aluno"] = data
        caso["status"] = "FINALIZADO"
        caso["faltas"] = int(data["faltas"])
        caso["urgencia"] = "INDEFINIDA"
        #cadastrar na base de dados
        casos.insert_one(caso)     
        return {"message": "Aluno cadastrado com sucesso"}, 201
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
        if data["RA"] != aluno["RA"]:
            aluno["RA"] = data["RA"]
        if data["endereco"] != aluno["endereco"]:
            aluno["endereco"] = data["endereco"]
        if data["dataNascimento"] != aluno["dataNascimento"]:
            aluno["dataNascimento"] = data["dataNascimento"]
        if data["telefone"] != aluno["telefone"]:
            aluno["telefone"] = data["telefone"]
        if data["telefone2"] != aluno["telefone2"]:
            aluno["telefone2"] = data["telefone2"]
        if data["responsavel"] != aluno["responsavel"]:
            aluno["responsavel"] = data["responsavel"]
        if data["responsavel2"] != aluno["responsavel2"]:
            aluno["responsavel2"] = data["responsavel2"]
        if data["utiliz_teg"] != aluno["utiliz_teg"]:
            aluno["utiliz_teg"] = data["utiliz_teg"]
        if data["faltas"] != aluno["faltas"]:
            aluno["faltas"] = data["faltas"]
            caso = casos.find_one({"aluno._id": ObjectId(aluno_id)})
            caso["faltas"] = int(data["faltas"])
            if caso["faltas"] > 20:
                caso["urgencia"] = "MEDIA"
            elif caso["faltas"] > 40:
                caso["urgencia"] = "ALTA"
            else: 
                caso["urgencia"] = "BAIXA"
            casos.update_one({"aluno._id": ObjectId(aluno_id)}, {"$set": caso})
        if data["RA"] == "Vazio" or data["nome"] == "Vazio" or data["turma"] == "Vazio":
            aluno["situacao"] = "INCOMPLETO"
        else:
            aluno["situacao"] = "COMPLETO"
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
            return {"message": "Aluno excluido com sucesso successfully"}, 200
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
    
@alunos_bp.route('/alunoBuscaAtiva/completo', methods=['GET'])
@jwt_required()
def getAlunosCompleto():
    try:
        alunos_list = []
        for alunos1 in alunos.find({"situacao": "COMPLETO"}):
            alunos1['_id'] = str(alunos1['_id'])
            alunos_list.append(alunos1)
        return jsonify(alunos_list), 200
    except Exception as e:
        return {"error": str(e)}, 500
    
@alunos_bp.route('/alunoBuscaAtiva/incompleto', methods=['GET'])
@jwt_required()
def getAlunosIncompleto():
    try:
        alunos_list = []
        for alunos1 in alunos.find({"situacao": "INCOMPLETO"}):
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
            tarefas = aluno["tarefas"]
            tarefas = update_status(tarefas)
            aluno["tarefas"] = tarefas
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
    


def update_status(tarefas):
    for tarefa in tarefas:
        if "dataFinal" in tarefa:
            prazo_final_str = tarefa["dataFinal"]
            
            prazo_final = datetime.datetime.fromisoformat(prazo_final_str.replace("Z", "+00:00"))
            if tarefa["status"] == "Finalizado":
                tarefa["status"] = "Finalizado"
            elif prazo_final < datetime.datetime.now(pytz.UTC) and tarefa["status"] != "Finalizdo":
                tarefa["status"] = "Atrasada"
            elif tarefa["status"] == "Em andamento" and prazo_final > datetime.datetime.now(pytz.UTC):
                tarefa["status"] = "Em andamento"   

            else:
                tarefa["status"] = "Em andamento"
    return tarefas


@alunos_bp.route('/alunoBuscaAtiva/pendencias', methods=['GET'])
def getPendencias():
    try:
        pend = alunos.count_documents({"situacao": "INCOMPLETO"})
        return jsonify({"pendencias": pend}), 200
    except Exception as e:
        return {"error": str(e)}, 500