# Sistema de Busca Ativa Escolar (SIBAE)


### Integrantes do grupo:
- Gustavo Barroso Souza Cruz
- Leonardo Freitas
- Rafaela Afférri de Oliveira
- Eduardo Takeiyaginuna
- Giovanny Russo Pinto
- Julia Almeida Silva

Em parceria com a EMEF Gonzaguinha, Heliópolis, São Paulo.


## Contexto para o projeto

Nossa sociedade ainda está lidando com as várias consequências da pandemia de COVID-19. Um desses desafios que se acentuou após a pandemia foi a evasão escolar, que apresentaram um aumento de 171% em comparação a 2019. 

Em setembro de 2023, a Secretaria Municipal de Educação de São Paulo (SME) estabeleceu o programa de Busca Ativa Escolar (BAE), com o objetivo de identificar e acompanhar crianças e adolescentes que estão fora da escola ou em risco de evasão. 
Esse programa tem se deparado com diversas dificuldades, principalmente em relação ao compartilhamento de informações entre agentes de busca e a escola, monitoramento do processo de busca e a falta de integração entre os sistemas de informação.


## Nossa Solução

O nosso sistema tenta resolver esses problemas enfrentados pelo programa de Busca Ativa Escolar. A nossa solução é um sistema de gerenciamento de busca ativa escolar, que tem como objetivo facilitar o processo de busca e monitoramento de crianças e adolescentes em situação de evasão escolar.

Fizemos isso por meio de um sistema que permite a participação conjunta de Professores, Agentes de Busca e Administradores da escola, de forma que cada um posssa contribuir com informações relevantes para o processo de busca e monitoramento.
Além disso, o sistema integra grande parte dos elementos desse processo, permitindo o monitoramento do progresso da busca e geração de relatórios para a Secretaria Municipal de Educação.


# Participação de diferentes atores no sistema:


## Professores:

Os professores podem atribuir tarefas para os alunos e atualizar o status de cada tarefa. Isso permite que os professores possam acompanhar o progresso dos alunos e provê informações relevantes para o relatório da busca ativa escolar.


## Agentes de Busca Ativa Escolar (ABAEs):

Os ABAEs têm acesso aos casos registrados de alunos e podem atualizar informações do caso, que são apresentadas na ficha do caso. Eles podem registrar visitas, ligações, atendimentos aos pais ou responsáveis e atualizar tarefas. 
Além disso, controlam o status e a urgência de cada caso, permitindo um controle de prioridades. 
Relatórios em PDF de casos podem ser gerados, com a opção de escolher quais ocorrências serão incluídas.


## Administradores:

Os administradores têm acesso a tudo que os ABAEs têm, mas também podem visualizar e editar os dados dos alunos, criar ou apagar alunos, acessar um dashboard com informações com informações relevantes sobre casos e gerenciar os usuários do sistema.


# Parte técnica:

Nós usamos React (JavaScript) para o front-end, Flask (Python) para o back-end e MongoDB para o banco de dados.