from ERP import database, login_manager
from datetime import datetime
from flask_login import UserMixin


class Usuarios(database.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(100), unique=True, nullable=False)
    senha = database.Column(database.String(300), nullable=False)
    acesso = database.Column(database.Integer, nullable=False)
    data_caadastro = database.Column(database.DateTime, default=datetime.utcnow().date())
    situacao = database.Column(database.Integer, database.ForeignKey('situacoes.id'), default=1)

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
    cep = database.Column(database.String(15))
    data_fundacao = database.Column(database.Date)
    cpf = database.Column(database.String(20))
    nome = database.Column(database.String(100))
    telefone = database.Column(database.String(20))
    telefone2 = database.Column(database.String(20))
    telefone3 = database.Column(database.String(20))
    email = database.Column(database.String(100))
    data_aniversario = database.Column(database.Date)
    data_cadastro = database.Column(database.DateTime, default=datetime.utcnow().date())
    tipo_cadastro = database.Column(database.Integer, database.ForeignKey('tipos_cadastro.id'), nullable=False)
    obs = database.Column(database.Text)

class TiposCadastros(database.Model):
    __tablename__ = 'tipos_cadastro'
    id = database.Column(database.Integer, primary_key=True)
    nome_tipo = database.Column(database.String(70))

