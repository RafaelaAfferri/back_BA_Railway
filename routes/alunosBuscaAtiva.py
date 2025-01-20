from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from bson.objectid import ObjectId
from config import alunos, casos
import datetime
import pytz
import pandas as pd

alunos_bp = Blueprint('alunos', __name__)

@alunos_bp.route('/alunoBuscaAtiva', methods=['POST'])
@jwt_required()
def registerAluno():
    try:
        # data = request.get_json()
        if 'file' not in request.files:
            return {"error": "Nenhum arquivo foi enviado"}, 400
        file = request.files['file']

        excel_file = pd.ExcelFile(file)
        sheet_names = excel_file.sheet_names
        dict_turmas = {}
        for sheet in sheet_names:
            
            df = pd.read_excel(file, sheet_name=sheet)
            #endereço, telefone, telefone2, responsavel2, faltas
            row = df.isin(["Turma"]).values.nonzero()[0][0]
            col = df.isin(["Turma"]).values.nonzero()[1][0]

            turma_info=df.iat[row, col + 1].split(" ")[2]

            dict_turmas[turma_info]=df

        dict_turmas_sorted = dict(sorted(dict_turmas.items(), reverse=True))

        # Agrupamento de turmas
        dfs_agrupados = {}
        for turma, df in dict_turmas_sorted.items():
            df_novo = df.iloc[3:].reset_index(drop=True)
            df_novo.columns = df_novo.iloc[0]
            df_novo = df_novo[1:].reset_index(drop=True)

            numero_turma = turma[0]  # Pega o primeiro caractere da turma
            if numero_turma not in dfs_agrupados:
                dfs_agrupados[numero_turma] = []
            # Adiciona uma coluna indicando a turma original
            df_novo['turma'] = turma
            dfs_agrupados[numero_turma].append(df_novo)
        dfs_finais = {}
        for numero, lista_dfs in dfs_agrupados.items():
            dfs_finais[numero] = pd.concat(lista_dfs, ignore_index=True)
        for key in dfs_finais:
            df = dfs_finais[key]
            #Remova a primeira linha, pois ela já virou o cabeçalho
            # df_novo = df.iloc[3:].reset_index(drop=True)
            # df_novo.columns = df_novo.iloc[0]
            # df_novo = df_novo[1:].reset_index(drop=True)

            nomes = df["Nome do Aluno"].tolist()
            ras = df["Ra Prodesp"].tolist()
            responsaveis1 = df["Filiação 1"].tolist()
            turmas = df["turma"].tolist()
            tegs = df["Utiliz. T.E.G."].tolist()
            
            alunos_list = alunos.find({"turma": { "$regex": f"^{key}", "$options": "i" }})
            #deleta alunos que não existem mais
            
            for aluno in alunos_list:
                if aluno["nome"] not in nomes:
                    casos.delete_one({"aluno._id": ObjectId(aluno["_id"])})
                    alunos.delete_one({"_id": ObjectId(aluno["_id"])})

            for i in range(len(nomes)):
                if alunos.find_one({"RA": ras[i]}):
                    data =  alunos.find_one({"RA": ras[i]})
                    data["nome"] = nomes[i]
                    data["turma"] = turmas[i]
                    data["responsavel"] = responsaveis1[i]
                    data['faltas'] = 0
                    data['Utiliz. T.E.G.'] = tegs[i]
                    alunos.update_one({"RA": ras[i]}, {"$set": data})
                    continue
                data = {}
                data["nome"] = nomes[i]
                data["RA"] = ras[i]
                data["turma"] = turmas[i]
                data["dataNascimento"] = ''
                data["tarefas"] = []
                data["endereco"] = ''
                data["telefone"] = ''
                data["telefone2"] = ''
                data["responsavel"] = responsaveis1[i]
                data["responsavel2"] = ''
                data["faltas"] = 0
                data["Utiliz. T.E.G."] = tegs[i]
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
        return {"message": "Alunos registrados com sucesso"}, 201
    except Exception as e:
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