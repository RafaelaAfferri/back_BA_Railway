import pymongo
import certifi
from datetime import timedelta

class CONFIG:
    JWT_SECRET_KEY = 'busca-ativa-escolar'
    JWT_EXPIRATION_DELTA = timedelta(days=15)
    MONGO_URI = 'mongodb+srv://admin:admin@cluster0.dc2vjrc.mongodb.net/buscaAtiva?retryWrites=true&w=majority'

client_mongo = pymongo.MongoClient(CONFIG.MONGO_URI, tlsCAFile=certifi.where())
accounts = client_mongo.buscaAtiva.accounts
tokens = client_mongo.buscaAtiva.tokens
casos = client_mongo.buscaAtiva.casos
alunos = client_mongo.buscaAtiva.alunos
