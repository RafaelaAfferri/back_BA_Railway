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
    MONGO_URI = load_dotenv("MONGO_URI")

client_mongo = pymongo.MongoClient(CONFIG.MONGO_URI, tlsCAFile=certifi.where())
accounts = client_mongo.buscaAtiva.accounts
tokens = client_mongo.buscaAtiva.tokens
casos = client_mongo.buscaAtiva.casos
alunos = client_mongo.buscaAtiva.alunos
