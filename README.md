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



# Rotas do back-end

# Alunos API

Esta API fornece um conjunto de endpoints para gerenciar estudantes (`alunos`) e seus casos associados (`casos`). A API é construída usando Flask e é protegida com JWT (JSON Web Tokens). Abaixo está uma explicação detalhada de cada rota e sua funcionalidade.

## Rotas

### Registrar um Novo Aluno

**Endpoint:** `/alunoBuscaAtiva`  
**Método:** `POST`  
**Descrição:** Registra um novo aluno na coleção `alunos` e cria um caso associado na coleção `casos`.  
**Autenticação:** JWT necessária  
**Corpo da Requisição:** Os dados do aluno, incluindo RA, nome, turma, endereço, telefone, e responsáveis.  

### Atualizar um Aluno Existente

**Endpoint:** `/alunoBuscaAtiva/<aluno_id>`  
**Método:** `PUT`  
**Descrição:** Atualiza os detalhes de um aluno existente na coleção `alunos`.  
**Autenticação:** JWT necessária  
**Corpo da Requisição:** Os dados atualizados do aluno, como nome, turma, endereço, telefone, e responsáveis.  

### Obter Aluno pelo RA

**Endpoint:** `/alunoBuscaAtiva/ra/<string:ra>`  
**Método:** `GET`  
**Descrição:** Recupera um aluno pelo seu RA (Número de Registro).  
**Autenticação:** JWT necessária  

### Deletar um Aluno

**Endpoint:** `/alunoBuscaAtiva/<aluno_id>`  
**Método:** `DELETE`  
**Descrição:** Deleta um aluno e seu caso associado da base de dados.  
**Autenticação:** JWT necessária  

### Obter Todos os Alunos

**Endpoint:** `/alunoBuscaAtiva`  
**Método:** `GET`  
**Descrição:** Recupera todos os alunos da coleção `alunos`.  
**Autenticação:** JWT necessária  

### Obter Aluno por ID

**Endpoint:** `/alunoBuscaAtiva/<aluno_id>`  
**Método:** `GET`  
**Descrição:** Recupera um aluno pelo seu ID na coleção `alunos`.  
**Autenticação:** JWT necessária  

### Obter Aluno pelo ID do Caso

**Endpoint:** `/alunoBuscaAtiva/caso/<caso_id>`  
**Método:** `GET`  
**Descrição:** Recupera um aluno pelo ID do seu caso na coleção `casos`.  
**Autenticação:** JWT necessária  

# Auth API

Esta API fornece um conjunto de endpoints para autenticação de usuários. A API é construída usando Flask, Flask-JWT-Extended para autenticação com tokens JWT e Flask-Bcrypt para hash de senhas. Um `BackgroundScheduler` da biblioteca APScheduler é usado para remover tokens expirados periodicamente. Abaixo está uma explicação detalhada de cada rota e sua funcionalidade.

## Rotas

### Login

**Endpoint:** `/login`  
**Método:** `POST`  
**Descrição:** Autentica um usuário com email e senha, e retorna um token de acesso JWT se a autenticação for bem-sucedida.  
**Corpo da Requisição:** Os dados de login do usuário, incluindo email e senha.  

### Logout

**Endpoint:** `/logout`  
**Método:** `POST`  
**Descrição:** Invalida o token de acesso JWT do usuário, efetivando o logout.  
**Autenticação:** JWT necessária  
**Corpo da Requisição:** O token JWT a ser invalidado.  

### Verificar Login

**Endpoint:** `/verificar-login`  
**Método:** `POST`  
**Descrição:** Verifica se o token de acesso JWT do usuário ainda é válido.  
**Autenticação:** JWT necessária  
**Corpo da Requisição:** O token JWT a ser verificado.  

# Casos API

Esta API fornece um conjunto de endpoints para gerenciar casos associados aos estudantes (`casos`). A API é construída usando Flask e é protegida com JWT (JSON Web Tokens). Abaixo está uma explicação detalhada de cada rota e sua funcionalidade.

## Rotas

### Obter Casos

**Endpoint:** `/casos`  
**Método:** `GET`  
**Descrição:** Recupera uma lista de casos. Permite filtros opcionais por `aluno_id` e `status`.  
**Autenticação:** JWT necessária  
**Parâmetros de Consulta:** 
- `aluno_id`: ID do aluno.
- `status`: Status do caso.

### Atualizar um Caso

**Endpoint:** `/casos/<string:id>`  
**Método:** `PUT`  
**Descrição:** Atualiza os detalhes de um caso existente na coleção `casos`.  
**Autenticação:** JWT necessária  
**Corpo da Requisição:** Os dados atualizados do caso, como ligações, visitas, atendimentos, status e urgência.

### Gerar Relatório

**Endpoint:** `/casos/gerar-relatorio`  
**Método:** `POST`  
**Descrição:** Gera um relatório em PDF com base nos dados fornecidos e retorna o arquivo PDF.  
**Autenticação:** JWT necessária  
**Corpo da Requisição:** Os dados necessários para gerar o relatório, incluindo informações da DRE, unidade escolar, endereço, contato, turma, estudante, RA, usuário, ligações, visitas e atendimentos.

# Tarefas API

Esta API fornece um conjunto de endpoints para gerenciar tarefas associadas aos alunos. A API é construída usando Flask e é protegida com JWT (JSON Web Tokens). Abaixo está uma explicação detalhada de cada rota e sua funcionalidade.

## Rotas

### Deletar Tarefa

**Endpoint:** `/tarefas/<string:id_aluno>/<string:id_tarefa>`  
**Método:** `DELETE`  
**Descrição:** Deleta uma tarefa específica de um aluno.  
**Autenticação:** JWT necessária  
**Parâmetros da URL:** 
- `id_aluno`: ID do aluno.
- `id_tarefa`: ID da tarefa a ser deletada.

### Registrar Tarefa

**Endpoint:** `/tarefas/<string:id>`  
**Método:** `POST`  
**Descrição:** Registra uma nova tarefa para um aluno.  
**Autenticação:** JWT necessária  
**Parâmetros da URL:** 
- `id`: ID do aluno.

**Corpo da Requisição:** Os dados da tarefa a ser registrada.

### Atualizar Tarefa

**Endpoint:** `/tarefas/<string:id_aluno>/<string:id_tarefa>`  
**Método:** `PUT`  
**Descrição:** Atualiza os detalhes de uma tarefa específica de um aluno.  
**Autenticação:** JWT necessária  
**Parâmetros da URL:** 
- `id_aluno`: ID do aluno.
- `id_tarefa`: ID da tarefa a ser atualizada.

**Corpo da Requisição:** Os dados atualizados da tarefa.

### Obter Tarefas

**Endpoint:** `/tarefas/<string:id_aluno>`  
**Método:** `GET`  
**Descrição:** Recupera todas as tarefas de um aluno específico.  
**Autenticação:** JWT necessária  
**Parâmetros da URL:** 
- `id_aluno`: ID do aluno.

# Usuários API

Esta API fornece um conjunto de endpoints para gerenciar usuários. A API é construída usando Flask e é protegida com JWT (JSON Web Tokens). Abaixo está uma explicação detalhada de cada rota e sua funcionalidade.

## Rotas

### Registrar Usuário

**Endpoint:** `/usuarios`  
**Método:** `POST`  
**Descrição:** Registra um novo usuário na coleção `accounts`.  
**Autenticação:** JWT necessária  
**Corpo da Requisição:** Os dados do usuário a ser registrado, incluindo email, senha, permissão e nome.

### Deletar Usuário

**Endpoint:** `/usuarios/<user_id>`  
**Método:** `DELETE`  
**Descrição:** Deleta um usuário específico da coleção `accounts`.  
**Autenticação:** JWT necessária  
**Parâmetros da URL:** 
- `user_id`: ID do usuário a ser deletado.

### Obter Usuários

**Endpoint:** `/usuarios`  
**Método:** `GET`  
**Descrição:** Recupera uma lista de todos os usuários na coleção `accounts`.  
**Autenticação:** JWT necessária

### Atualizar Usuário

**Endpoint:** `/usuarios/<user_id>`  
**Método:** `PUT`  
**Descrição:** Atualiza os detalhes de um usuário específico na coleção `accounts`.  
**Autenticação:** JWT necessária  
**Parâmetros da URL:** 
- `user_id`: ID do usuário a ser atualizado.

**Corpo da Requisição:** Os dados atualizados do usuário, como email, nome e permissão.

### Obter Permissão do Usuário

**Endpoint:** `/usuarios-permissao`  
**Método:** `POST`  
**Descrição:** Retorna o tipo de permissão do usuário, determinando o que ele pode acessar.  
**Autenticação:** JWT necessária  
**Corpo da Requisição:** O token de autenticação do usuário.

### Obter Dados do Usuário

**Endpoint:** `/usuarios-dados`  
**Método:** `POST`  
**Descrição:** Retorna os dados do usuário.  
**Autenticação:** JWT necessária  
**Corpo da Requisição:** O token de autenticação do usuário.

## Funções de Utilidade

### Gerar PDF

**Função:** `generate_pdf`  
**Descrição:** Gera um arquivo PDF a partir do contexto fornecido.

### Remover Tokens Expirados

**Função:** `remove_expired_tokens`  
**Descrição:** Remove tokens expirados da coleção `tokens`.  
**Agendamento:** A função é executada a cada 60 minutos usando um `BackgroundScheduler`.  

### Inicialização do Scheduler

O `BackgroundScheduler` é iniciado para executar a função de remoção de tokens expirados a cada 60 minutos. O scheduler é finalizado automaticamente quando a aplicação é encerrada.

