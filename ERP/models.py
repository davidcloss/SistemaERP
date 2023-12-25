from ERP import database, login_manager
from datetime import datetime
from flask_login import UserMixin


class Usuarios(database.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(100), unique=True, nullable=False)
    senha = database.Column(database.String(300), nullable=False)
    data_cadastro = database.Column(database.DateTime, default=datetime.utcnow())
    situacao = database.Column(database.Integer, database.ForeignKey('situacoes_usuarios.id'), default=1)
    tipo_usuario = database.Column(database.Integer, database.ForeignKey('tipos_usuarios.id'), nullable=False)

class SituacoesUsuarios(database.Model):
    __tablename__ = 'situacoes_usuarios'
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
#TODO: Criar gênero roupa

class TiposRoupas(database.Model):
    __tablename__ = 'tipos_roupas'
    id = database.Column(database.Integer, primary_key=True)
    nome_tipo_roupa = database.Column(database.String(100), nullable=False, unique=True)

class Cores(database.Model):
    __tablename__ = 'cores'
    id = database.Column(database.Integer, primary_key=True)
    nome_cor = database.Column(database.String, nullable=False, unique=True)

class Tamanhos(database.Model):
    __tablename__ = 'tamanhos'
    id = database.Column(database.Integer, primary_key=True)
    nome_tamanho = database.Column(database.String, nullable=False, unique=True)

class Marcas(database.Model):
    __tablename__ = 'marcas'
    id = database.Column(database.Integer, primary_key=True)
    nome_marca = database.Column(database.String, nullable=False, unique=True)

class TiposUnidades(database.Model):
    __tablename__ = 'tipos_unidades'
    id = database.Column(database.Integer, primary_key=True)
    nome_tipo_unidade = database.Column(database.String, nullable=False, unique=True)

class ItensEstoque(database.Model):
    __tablename__ = 'itens_estoque'
    id = database.Column(database.Integer, primary_key=True)
    id_tipo_roupa = database.Column(database.Integer, database.ForeignKey('tipos_roupas.id'), nullable=False)
    id_tamanho = database.Column(database.Integer, database.ForeignKey('tamanhos.id'), nullable=False)
    id_marca = database.Column(database.Integer, database.ForeignKey('marcas.id'), nullable=False)
    id_cor = database.Column(database.Integer, database.ForeignKey('cores.id'), nullable=False)
    codigo_item = database.Column(database.String(100), unique=True)
    data_cadastro = database.Column(database.DateTime, default=datetime.utcnow())
    data_ultima_entrada = database.Column(database.DateTime)
    data_ultima_saida = database.Column(database.DateTime)
    id_tipo_unidade = database.Column(database.Integer, database.ForeignKey('tipos_unidades.id'), nullable=False)
    qtd = database.Column(database.Float)
    valor_estoque_custo = database.Column(database.Float)
    valor_unitario_medio_custo = database.Column(database.Float)
    valor_estoque_venda = database.Column(database.Float)
    valor_unitario_medio_venda = database.Column(database.Float)
    qtd_minima = database.Column(database.Float)

class TiposTransacoesEstoque(database.Model):
    __tablename__ = 'tipos_transacoes'
    id = database.Column(database.Integer, primary_key=True)
    nome_tipo_transacao = database.Column(database.String, nullable=False, unique=True)

class TransacoesEstoque(database.Model):
    __tablename__ = 'transacoes_estoque'
    id = database.Column(database.Integer, primary_key=True)
    id_lote = database.Column(database.Integer)
    tipo_transacao = database.Column(database.Integer, database.ForeignKey('tipos_transacoes.id'), nullable=False)
    data_transacao = database.Column(database.DateTime)
    data_registro_transacao = database.Column(database.DateTime, default=datetime.utcnow())
    id_item = database.Column(database.Integer, database.ForeignKey('itens_estoque.id'))
    qtd_transacao = database.Column(database.Integer, nullable=False)
    valor_unitario_medio_custo = database.Column(database.Float, nullable=False)
    valor_total_transacao_custo = database.Column(database.Float, nullable=False)
    valor_unitario_medio_venda = database.Column(database.Float, nullable=False)
    valor_total_transacao_venda = database.Column(database.Float, nullable=False)

class Bancos(database.Model):
    __tablename__ = 'bancos'
    id = database.Column(database.Integer, primary_key=True)
    cod_banco = database.Column(database.Integer, unique=True, nullable=False)
    nome_banco = database.Column(database.String, unique=True, nullable=False)

class AgenciaBanco(database.Model):
    __tablename__ = 'agencia_bancos'
    id = database.Column(database.Integer, primary_key=True)
    agencia = database.Column(database.Integer, unique=True)
    digito_agencia = database.Column(database.Integer)
    id_banco = database.Column(database.Integer, database.ForeignKey('bancos.id'))
    apelido_agencia = database.Column(database.String, unique=True)
    id_cliente = database.Column(database.Integer, database.ForeignKey('clientes_fornecedores.id'))

class ContasBancarias(database.Model):
    __tablename__ = 'contas_bancarias'
    id = database.Column(database.Integer, primary_key=True)
    id_agencia = database.Column(database.Integer, database.ForeignKey('agencia_bancos.id'))
    apelido_conta = database.Column(database.String, unique=True)
    nro_conta = database.Column(database.Integer)
    digito_conta = database.Column(database.Integer)
    id_titular_conta = database.Column(database.Integer, database.ForeignKey('agencia_bancos.id'))
    cheque_especial = database.Column(database.Float, default=0)
    cheque_especial_utilizado = database.Column(database.Float, default=0)
    cheque_especial_disponivel = database.Column(database.Float, default=0)
    saldo_conta = database.Column(database.Float, default=0)
    situacao_conta = database.Column(database.Integer, default=1) #1- Ativo, 2 - Arquivada

class CartaoCredito(database.Model):
    __tablename__ = 'cartao_credito'
    id = database.Column(database.Integer, primary_key=True)
    id_conta_bancaria = database.Column(database.Integer, database.ForeignKey('agencia_bancos.id'))
    apelido_cartao = database.Column(database.String, unique=True)
    dia_inicial = database.Column(database.Integer, nullable=False)
    dia_final = database.Column(database.Integer, nullable=False)
    dia_pgto = database.Column(database.Integer, nullable=False)
    valor_limite = database.Column(database.Float, nullable=False)
    valor_gasto = database.Column(database.Float, default=0)
    valor_disponivel = database.Column(database.Float)

class FaturaCartaoCredito(database.Model):
    __tablename__ = 'fatura_cartao_credito'
    id = database.Column(database.Integer, primary_key=True)
    id_cartao_credito = database.Column(database.Integer, database.ForeignKey('cartao_credito.id'))
    valor_fatura = database.Column(database.Float, default=0)
    data_inicial = database.Column(database.Date)
    data_final = database.Column(database.Date)
    data_vcto = database.Column(database.Date)
    data_pgto = database.Column(database.Date)
    descontos_recebidos = database.Column(database.Float, default=0)
    juros_pagos = database.Column(database.Float, default=0)
    valor_pago = database.Column(database.Float)
    situacao_fatura = database.Column(database.Integer, default=0)# 0 - Em aberto, 1 - Pago,
    # 2 - Em atraso, 3 - Pago em atraso
