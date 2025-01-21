import pymongo
import certifi
import datetime
import os
from dotenv import load_dotenv

load_dotenv()


class CONFIG:
    JWT_SECRET_KEY = 'busca-ativa-escolar'
    JWT_VERIFY_EXPIRATION = True
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(days=10)
    MONGO_URI = 'mongodb+srv://admin:admin@ba.auiky.mongodb.net/buscaAtiva?retryWrites=true&w=majority'


print(CONFIG.MONGO_URI)


client_mongo = pymongo.MongoClient(CONFIG.MONGO_URI, tlsCAFile=certifi.where())
accounts = client_mongo.buscaAtiva.accounts
tokens = client_mongo.buscaAtiva.tokens
casos = client_mongo.buscaAtiva.casos
alunos = client_mongo.buscaAtiva.alunos
