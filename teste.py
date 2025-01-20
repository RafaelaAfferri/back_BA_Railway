import pandas as pd

# Exemplo de dicionário
dados = {
    "4a": pd.DataFrame({"aluno": ["Iara", "João"], "nota": [10, 8]}),
    "3a": pd.DataFrame({"aluno": ["Ana", "Carlos"], "nota": [8, 9]}),
    "3b": pd.DataFrame({"aluno": ["Bruno", "Débora"], "nota": [7, 10]}),
    "2a": pd.DataFrame({"aluno": ["Eva", "Fernando"], "nota": [6, 8]}),
    "2b": pd.DataFrame({"aluno": ["Gustavo", "Helena"], "nota": [9, 7]}),
    "4b": pd.DataFrame({"aluno": ["Karina", "Lucas"], "nota": [7, 9]}),
    "4c": pd.DataFrame({"aluno": ["Marcos", "Nina"], "nota": [6, 8]})
}

# Agrupamento de turmas
dfs_agrupados = {}
for turma, df in dados.items():
    numero_turma = turma[0]  # Pega o primeiro caractere da turma
    if numero_turma not in dfs_agrupados:
        dfs_agrupados[numero_turma] = []
    # Adiciona uma coluna indicando a turma original
    df['turma'] = turma
    dfs_agrupados[numero_turma].append(df)

# Concatenar os DataFrames para cada número de turma
dfs_finais = {}
for numero, lista_dfs in dfs_agrupados.items():
    dfs_finais[numero] = pd.concat(lista_dfs, ignore_index=True)

# Exibindo os DataFrames agrupados
for numero, df in dfs_finais.items():
    print(f"Turmas que começam com {numero}:")
    print(df)
    print()
