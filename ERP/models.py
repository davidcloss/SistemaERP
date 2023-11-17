from ERP import database, login_manager
from datetime import datetime
from flask_login import UserMixin


class Usuarios(database.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(100), unique=True, nullable=False)
    senha = database.Column(database.String(300), nullable=False)
    data_cadastro = database.Column(database.DateTime, default=datetime.utcnow())
    situacao = database.Column(database.Integer, database.ForeignKey('situacoes.id'), default=1)
    tipo_usuario = database.Column(database.Integer, database.ForeignKey('tipos_usuarios.id'), nullable=False)

class SituacoesUsuarios(database.Model):
    __tablename__ = 'situacoes'
    id = database.Column(database.Integer, primary_key=True)
    nome_situacao = database.Column(database.String(70))
    situacoes_usuarios = database.relationship('Usuarios', backref='situacoes_usuarios', lazy=True)

class ClientesFornecedores(database.Model):
    __tablename__ ='clientes_fornecedores'
    id = database.Column(database.Integer, primary_key=True)
    nome_fantasia = database.Column(database.String(500))
    razao_social = database.Column(database.String(500))
    cnpj = database.Column(database.String(20), unique=True)
    rua = database.Column(database.String(100))
    complemento = database.Column(database.String(70))
    nro = database.Column(database.String(20))
    bairro = database.Column(database.String(70))
    cidade = database.Column(database.String(70))
    uf = database.Column(database.String(2))
    cep = database.Column(database.String(15))
    data_fundacao = database.Column(database.Date)
    cpf = database.Column(database.String(20), unique=True)
    nome = database.Column(database.String(100))
    telefone = database.Column(database.String(20))
    telefone2 = database.Column(database.String(20))
    telefone3 = database.Column(database.String(20))
    email = database.Column(database.String(100))
    data_aniversario = database.Column(database.Date)
    obs = database.Column(database.Text)
    data_cadastro = database.Column(database.DateTime, default=datetime.utcnow())
    tipo_cadastro = database.Column(database.Integer, database.ForeignKey('tipos_cadastro.id'), nullable=False)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False)

class TiposCadastros(database.Model):
    __tablename__ = 'tipos_cadastro'
    id = database.Column(database.Integer, primary_key=True)
    nome_tipo = database.Column(database.String(70), nullable=False, unique=True)
    tipos_cadastro = database.relationship('ClientesFornecedores', backref='cadastros_tipos', lazy=True)

class TiposUsuarios(database.Model):
    __tablename__ = 'tipos_usuarios'
    id = database.Column(database.Integer, primary_key=True)
    nome_tipo = database.Column(database.String(70), nullable=False, unique=True)
    tipos_usuarios = database.relationship('Usuarios', backref='usuarios_tipo', lazy=True)



class CadastroEmpresa(database.Model):
    __tablename__ = 'cadastro_empresa'
    id = database.Column(database.Integer, primary_key=True)
    nome_empresa = database.Column(database.String(100), nullable=False)
    email_verificaco = database.Column(database.String(100), nullable=False)
    situacao = database.Column(database.Integer, default='A')

class TiposRoupas(database.Model):
    __table_name__ = 'tipos_roupas'
    id = database.Column(database.Integer, primary_key=True)
    nome_tipo_roupa = database.Column(database.String)

class ItensEstoque(database.Model):
    __tablename__ = 'itens_estoque'
    id = database.Column(database.Integer, primary_key=True)
    id_tipo_roupa = database.Column(database.Integer, database.ForeignKey('tipos_roupas.id'), nullable=False)
    id_tamanho = database.Column(database.Integer, database.ForeignKey('tamanhos.id'), nullable=False)
    id_marca = database.Column(database.Integer, database.ForeignKey('marcas.id'), nullable=False)
    id_cor = database.Column(database.Integer, database.ForeignKey('cores.id'), nullable=False)
    data_cadastro = database.Column(database.DateTime, default=datetime.utcnow())
    data_ultima_entrada = database.Column(database.DateTime)
    data_ultima_saida = database.Column(database.DateTime)
    qtd = database.Column(database.Float)
    valor_estoque = database.Column(database.Float)
    valor_unitario_medio = database.Column(database.Float)
    qtd_minima = database.Column(database.Float)
