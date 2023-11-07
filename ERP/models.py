from ERP import database, login_manager
from datetime import datetime
from flask_login import UserMixin


class Usuarios(database.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(100), unique=True, nullable=False)
    senha = database.Column(database.String(300), nullable=False)
    data_caadastro = database.Column(database.DateTime, default=datetime.utcnow().date())
    ##TODO: situacao = database.Column(database.Integer, default=1)

class Situacoes(database.Model):
    __tablename__ = 'situacoes'
    id = database.Column(database.Integer, primary_key=True)
    nome_situacao = database.Column(database.String(70))

class ClientesFornecedores(database.Model):
    __tablename__ ='clientes_fornecedores'
    id = database.Column(database.Integer, primary_key=True)
    nome_fantasia = database.Column(database.String(500))
    razao_social = database.Column(database.String(500))
    cnpj = database.Column(database.String(20))
    rua = database.Column(database.String(100))
    complemento = database.Column(database.String(70))
    nro = database.Column(database.String(20))
    bairro = database.Column(database.String(70))
    cidade = database.Column(database.String(70))
    uf = database.Column(database.String(2))
    cpf = database.Column(database.String(20))
    nome = database.Column(database.String(100))
    data_cadastro = database.Column(database.DateTime, dafault=datetime.utcnow().date())
    ##TODO: tipo_cadastro = database.Column(database.String(500))

class TiposCadastros(database.Model):
    __tablename__ = 'tipos_cadastro'
    id = database.Column(database.Integer, primary_key=True)
    nome_tipo = database.Column(database.String(70))

class ContatosClientesFornecedores(database.Model):
    __tablename__ = 'contatos_clientes_fornecedores'
    id = database.Column(database.Integer, primary_key=True)
#TODO: resto