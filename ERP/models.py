from ERP import database, login_manager
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import text  # Importar o método 'text' para comandos SQL nativos
from sqlalchemy.sql import func


class TiposUsuarios(database.Model):
    __tablename__ = 'tipos_usuarios'
    id = database.Column(database.Integer, primary_key=True)
    nome_tipo = database.Column(database.String(70), nullable=False, unique=True)
    tipos_usuarios = database.relationship('Usuarios', backref='usuarios_tipo', lazy=True)
    situacao = database.Column(database.Integer, default=1)  # 1 - ativo 2 - inativo


class SituacoesUsuarios(database.Model):
    __tablename__ = 'situacoes_usuarios'
    id = database.Column(database.Integer, primary_key=True)
    nome_situacao = database.Column(database.String(70))
    situacoes_usuarios = database.relationship('Usuarios', backref='situacoes_usuarios', lazy=True)


class Usuarios(database.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(100), unique=True, nullable=False)
    senha = database.Column(database.String(300), nullable=False)
    data_cadastro = database.Column(database.DateTime)
    situacao = database.Column(database.Integer, database.ForeignKey('situacoes_usuarios.id'), default=1)
    tipo_usuario = database.Column(database.Integer, database.ForeignKey('tipos_usuarios.id'), nullable=False)
    status_tickets = database.relationship('StatusTickets', backref='usuario', cascade='all, delete-orphan')


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
    data_fundacao = database.Column(database.DateTime)
    cpf = database.Column(database.String(20), unique=True)
    nome = database.Column(database.String(100))
    telefone = database.Column(database.String(20))
    telefone2 = database.Column(database.String(20))
    telefone3 = database.Column(database.String(20))
    email = database.Column(database.String(100))
    data_aniversario = database.Column(database.DateTime)
    obs = database.Column(database.Text)
    data_cadastro = database.Column(database.DateTime)
    tipo_cadastro = database.Column(database.Integer, database.ForeignKey('tipos_cadastro.id'), nullable=False)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False)
    situacao = database.Column(database.Integer, default=1)# 1 - ativo 2 - inativo

    def __str__(self):
        return f"<ClientesFornecedores(id={self.id}, nome_fantasia={self.nome_fantasia}, razao_social={self.razao_social}, cnpj={self.cnpj})>"


class TiposCadastros(database.Model):
    __tablename__ = 'tipos_cadastro'
    id = database.Column(database.Integer, primary_key=True)
    nome_tipo = database.Column(database.String(70), nullable=False, unique=True)
    tipos_cadastro = database.relationship('ClientesFornecedores', backref='cadastros_tipos', lazy=True)
    data_cadastro = database.Column(database.DateTime)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False, default=1)
    situacao = database.Column(database.Integer, default=1)  # 1 - ativo 2 - inativo


class CadastroEmpresa(database.Model):
    __tablename__ = 'cadastro_empresa'
    id = database.Column(database.Integer, primary_key=True)
    nome_empresa = database.Column(database.String(100), nullable=False)
    email_verificaco = database.Column(database.String(100), nullable=False)
    situacao = database.Column(database.Integer, default='A')
    data_cadastro = database.Column(database.DateTime)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False,
                                          default=1)



class GeneroRoupa(database.Model):
    __tablename__ = 'genero_roupa'
    id = database.Column(database.Integer, primary_key=True)
    nome_genero = database.Column(database.String, nullable=False, unique=True)
    data_cadastro = database.Column(database.DateTime)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False,
                                          default=1)
    situacao = database.Column(database.Integer, default=1)  # 1 - ativo 2 - inativo


class TiposRoupas(database.Model):
    __tablename__ = 'tipos_roupas'
    id = database.Column(database.Integer, primary_key=True)
    nome_tipo_roupa = database.Column(database.String(100), nullable=False, unique=True)
    data_cadastro = database.Column(database.DateTime)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False,
                                          default=1)
    situacao = database.Column(database.Integer, default=1)  # 1 - ativo 2 - inativo


class Cores(database.Model):
    __tablename__ = 'cores'
    id = database.Column(database.Integer, primary_key=True)
    nome_cor = database.Column(database.String, nullable=False, unique=True)
    data_cadastro = database.Column(database.DateTime)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False,
                                          default=1)
    situacao = database.Column(database.Integer, default=1)  # 1 - ativo 2 - inativo


class Tamanhos(database.Model):
    __tablename__ = 'tamanhos'
    id = database.Column(database.Integer, primary_key=True)
    nome_tamanho = database.Column(database.String, nullable=False, unique=True)
    data_cadastro = database.Column(database.DateTime)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False,
                                          default=1)
    situacao = database.Column(database.Integer, default=1)  # 1 - ativo 2 - inativo


class Marcas(database.Model):
    __tablename__ = 'marcas'
    id = database.Column(database.Integer, primary_key=True)
    nome_marca = database.Column(database.String, nullable=False, unique=True)
    data_cadastro = database.Column(database.DateTime)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False,
                                          default=1)
    situacao = database.Column(database.Integer, default=1)  # 1 - ativo 2 - inativo


class TiposUnidades(database.Model):
    __tablename__ = 'tipos_unidades'
    id = database.Column(database.Integer, primary_key=True)
    nome_tipo_unidade = database.Column(database.String, nullable=False, unique=True)
    data_cadastro = database.Column(database.DateTime)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False,
                                          default=1)
    situacao = database.Column(database.Integer, default=1)  # 1 - ativo 2 - inativo


class ItensEstoque(database.Model):
    __tablename__ = 'itens_estoque'
    id = database.Column(database.Integer, primary_key=True)
    id_tipo_roupa = database.Column(database.Integer, database.ForeignKey('tipos_roupas.id'), nullable=False)
    id_tamanho = database.Column(database.Integer, database.ForeignKey('tamanhos.id'), nullable=False)
    id_marca = database.Column(database.Integer, database.ForeignKey('marcas.id'), nullable=False)
    id_cor = database.Column(database.Integer, database.ForeignKey('cores.id'), nullable=False)
    id_genero = database.Column(database.Integer, database.ForeignKey('genero_roupa.id'), nullable=False)
    codigo_item = database.Column(database.String(100), unique=True)
    data_cadastro = database.Column(database.DateTime)
    data_ultima_entrada = database.Column(database.DateTime)
    data_ultima_saida = database.Column(database.DateTime)
    id_tipo_unidade = database.Column(database.Integer, database.ForeignKey('tipos_unidades.id'), nullable=False)
    qtd = database.Column(database.Float)
    qtd_cond = database.Column(database.Float, default=0)
    qtd_disponivel = database.Column(database.Float, default=0)
    valor_estoque_custo = database.Column(database.Float)
    valor_unitario_medio_custo = database.Column(database.Float)
    valor_estoque_venda = database.Column(database.Float)
    valor_unitario_venda = database.Column(database.Float)
    qtd_minima = database.Column(database.Float)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False,
                                          default=1)
    situacao = database.Column(database.Integer, default=1)  # 1 - ativo 2 - inativo


class TiposTransacoesEstoque(database.Model):
    __tablename__ = 'tipos_transacoes'
    id = database.Column(database.Integer, primary_key=True)
    nome_tipo_transacao = database.Column(database.String, nullable=False, unique=True)
    data_cadastro = database.Column(database.DateTime)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False,
                                          default=1)
    situacao = database.Column(database.Integer, default=1)  # 1 - ativo 2 - inativo


class TransacoesEstoque(database.Model):
    __tablename__ = 'transacoes_estoque'
    id = database.Column(database.Integer, primary_key=True)
    id_lote = database.Column(database.Integer)
    id_ticket = database.Column(database.Integer, database.ForeignKey('tickets_comerciais.id'))
    tipo_transacao = database.Column(database.Integer, database.ForeignKey('tipos_transacoes.id'), nullable=False)
    data_transacao = database.Column(database.DateTime)
    data_registro_transacao = database.Column(database.DateTime, default=datetime.utcnow())
    id_item = database.Column(database.Integer, database.ForeignKey('itens_estoque.id'))
    qtd_transacao = database.Column(database.Integer, nullable=False)
    valor_unitario_medio_custo = database.Column(database.Float, nullable=False, default=0)
    valor_total_transacao_custo = database.Column(database.Float, nullable=False, default=0)
    valor_unitario_venda = database.Column(database.Float, nullable=False, default=0)
    valor_total_transacao_venda = database.Column(database.Float, nullable=False, default=0)
    data_cadastro = database.Column(database.DateTime)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False,
                                          default=1)
    situacao = database.Column(database.Integer, default=1)  # 1 - ativo 2 - inativo


class Bancos(database.Model):
    __tablename__ = 'bancos'
    id = database.Column(database.Integer, primary_key=True)
    cod_banco = database.Column(database.Integer, unique=True, nullable=False)
    nome_banco = database.Column(database.String, unique=True, nullable=False)
    data_cadastro = database.Column(database.DateTime)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False,
                                          default=1)
    situacao = database.Column(database.Integer, default=1)  # 1 - ativo 2 - inativo


class AgenciaBanco(database.Model):
    __tablename__ = 'agencia_bancos'
    id = database.Column(database.Integer, primary_key=True)
    agencia = database.Column(database.String)
    digito_agencia = database.Column(database.String)
    id_banco = database.Column(database.Integer, database.ForeignKey('bancos.id'))
    apelido_agencia = database.Column(database.String, unique=True)
    id_cliente = database.Column(database.Integer, database.ForeignKey('clientes_fornecedores.id'))
    data_cadastro = database.Column(database.DateTime)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False,
                                          default=1)
    situacao = database.Column(database.Integer, default=1)  # 1 - ativo 2 - inativo


class ContasBancarias(database.Model):
    __tablename__ = 'contas_bancarias'
    id = database.Column(database.Integer, primary_key=True)
    #  1 - Conta Caixa
    #  2 - Conta Bancária
    #  3 - Conta Máquina Cartão
    id_tipo_conta = database.Column(database.Integer)
    id_agencia = database.Column(database.Integer, database.ForeignKey('agencia_bancos.id'))
    apelido_conta = database.Column(database.String, unique=True)
    nro_conta = database.Column(database.String)
    digito_conta = database.Column(database.String)
    id_titular = database.Column(database.Integer, database.ForeignKey('agencia_bancos.id'))
    cheque_especial = database.Column(database.Float, default=0)
    cheque_especial_utilizado = database.Column(database.Float, default=0)
    cheque_especial_disponivel = database.Column(database.Float, default=0)
    saldo_conta = database.Column(database.Float, default=0)
    situacao_conta = database.Column(database.Integer, default=1) #1- Ativo, 2 - Arquivada
    data_cadastro = database.Column(database.DateTime)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False,
                                          default=1)
    situacao = database.Column(database.Integer, default=1)  # 1 - ativo 2 - inativo


class Cheques(database.Model):
    __tabelname__ = 'cheques'
    # 1 - Cheques Próprios terão vinculação com um id_conta
    # 2 - Chequs terceiros terão dados de conta e demais dados cadastrados indivualmente
    id = database.Column(database.Integer, primary_key=True)
    ## TIPO CHEQUE ##
    # 1 - Próprio
    # 2 - Terceiro
    id_tipo_cheque = database.Column(database.Integer, nullable=False)
    id_titular_cheque = database.Column(database.Integer, database.ForeignKey('clientes_fornecedores.id'))
    id_conta = database.Column(database.Integer, database.ForeignKey('contas_bancarias.id'))
    comp = database.Column(database.String)
    banco = database.Column(database.String)
    agencia = database.Column(database.String)
    conta = database.Column(database.String)
    serie = database.Column(database.String)
    nro_cheque = database.Column(database.String)
    valor_cheque = database.Column(database.Float)
    bom_para = database.Column(database.DateTime)
    data_emissao = database.Column(database.DateTime)
    compensado_em = database.Column(database.DateTime)
    ## SITUACAO CHEQUE ##
    # 0 - Em aberto: O cheque foi emitido, mas ainda não foi entregue ao beneficiário ou descontado.
    # 1 - Emitido: O cheque foi preenchido e entregue pelo emitente ao beneficiário.
    # 2 - Descontado: O beneficiário apresentou o cheque a um banco para recebimento imediato dos fundos, geralmente em troca de uma taxa.
    # 3 - Compensado: O cheque foi processado pelo banco e os fundos foram transferidos da conta do emitente para a conta do beneficiário.
    # 4 - Devolvido: O cheque foi devolvido pelo banco por algum motivo, como insuficiência de fundos, assinatura inválida, ou outras irregularidades.
    # 5 - Sustado: O emitente solicitou ao banco a suspensão do pagamento do cheque antes que ele fosse descontado ou compensado.
    # 6 - Cancelado: O cheque foi cancelado pelo emitente antes de ser entregue ao beneficiário ou foi destruído.
    # 7 - Prescrito: O cheque não foi apresentado para pagamento dentro do prazo legal (geralmente 30 dias para cheques emitidos na mesma praça e 60 dias para cheques emitidos em outra praça).
    # 8 - Extraviado: O cheque foi perdido ou roubado antes de ser descontado ou compensado.
    # 9 - Pré-datado: O cheque foi emitido com uma data futura e o beneficiário deve esperar até essa data para apresentá-lo ao banco.
    situacao_cheque = database.Column(database.Integer)
    data_cadastro = database.Column(database.DateTime)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False,
                                          default=1)
    

class TemporarioCheques(database.Model):
    __tablename__ = 'temporario_cheques'
    id = database.Column(database.Integer, primary_key=True)
    id_tipo_cheque = database.Column(database.Integer, nullable=False)
    id_titular_cheque = database.Column(database.Integer, database.ForeignKey('clientes_fornecedores.id'))
    id_conta = database.Column(database.Integer, database.ForeignKey('contas_bancarias.id'))
    comp = database.Column(database.String)
    banco = database.Column(database.String)
    agencia = database.Column(database.String)
    conta = database.Column(database.String)
    serie = database.Column(database.String)
    valor_cheque = database.Column(database.Float)
    data_emissao = database.Column(database.Float)
    bom_para = database.Column(database.DateTime)
    ## SITUACAO CHEQUE ##
    # 1 - Emitido: O cheque foi preenchido e entregue pelo emitente ao beneficiário.
    # 2 - Descontado: O beneficiário apresentou o cheque a um banco para recebimento imediato dos fundos, geralmente em troca de uma taxa.
    # 3 - Compensado: O cheque foi processado pelo banco e os fundos foram transferidos da conta do emitente para a conta do beneficiário.
    # 4 - Devolvido: O cheque foi devolvido pelo banco por algum motivo, como insuficiência de fundos, assinatura inválida, ou outras irregularidades.
    # 5 - Sustado: O emitente solicitou ao banco a suspensão do pagamento do cheque antes que ele fosse descontado ou compensado.
    # 6 - Cancelado: O cheque foi cancelado pelo emitente antes de ser entregue ao beneficiário ou foi destruído.
    # 7 - Prescrito: O cheque não foi apresentado para pagamento dentro do prazo legal (geralmente 30 dias para cheques emitidos na mesma praça e 60 dias para cheques emitidos em outra praça).
    # 8 - Extraviado: O cheque foi perdido ou roubado antes de ser descontado ou compensado.
    # 9 - Pré-datado: O cheque foi emitido com uma data futura e o beneficiário deve esperar até essa data para apresentá-lo ao banco.
    situacao_cheque = database.Column(database.Integer)


class CartaoCredito(database.Model):
    __tablename__ = 'cartao_credito'
    id = database.Column(database.Integer, primary_key=True)
    id_conta_bancaria = database.Column(database.Integer, database.ForeignKey('contas_bancarias.id'))
    apelido_cartao = database.Column(database.String, unique=True)
    dia_inicial = database.Column(database.Integer, nullable=False)
    dia_final = database.Column(database.Integer, nullable=False)
    dia_pgto = database.Column(database.Integer, nullable=False)
    valor_limite = database.Column(database.Float, nullable=False)
    valor_gasto = database.Column(database.Float, default=0)
    valor_disponivel = database.Column(database.Float)
    situacao_cartao = database.Column(database.Integer, default=1)# 1 - Ativo,
    # 2 - Bloqueado, 3 - Temporariamente Bloqueado
    data_cadastro = database.Column(database.DateTime)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False,
                                          default=1)
    situacao = database.Column(database.Integer, default=1)  # 1 - ativo 2 - inativo


class FaturaCartaoCredito(database.Model):
    __tablename__ = 'fatura_cartao_credito'
    id = database.Column(database.Integer, primary_key=True)
    cod_fatura = database.Column(database.String, unique=True, nullable=False)
    id_cartao_credito = database.Column(database.Integer, database.ForeignKey('cartao_credito.id'))
    valor_fatura = database.Column(database.Float, default=0)
    data_inicial = database.Column(database.DateTime)
    data_final = database.Column(database.DateTime)
    data_vcto = database.Column(database.DateTime)
    data_pagamento = database.Column(database.DateTime)
    multa_descontos_recebidos = database.Column(database.Float, default=0)
    valor_pago = database.Column(database.Float, default=0)
    situacao_fatura = database.Column(database.Integer, default=0)# 0 - Em aberto, 1 - Pago,
    # 2 - Em atraso, 3 - Pago em atraso, 4 - Pago parcial, 5 Pago parcial em Atraso
    data_cadastro = database.Column(database.DateTime)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False,
                                          default=1)


class CategoriasFinanceiras(database.Model):
    __tablename__ = 'categorias_financeiras'
    id = database.Column(database.Integer, primary_key=True)
    nome_categoria = database.Column(database.String(50), unique=True)
    tipo_transacao_financeira = database.Column(database.Integer, nullable=False) #0 -  Não aplicável 1 - Receita 2 - Custo 3 - Despesa 4 - Transferência +, 5 - Transferência -
    situacao = database.Column(database.Integer, default=1) #1 - ativo 2 - inativo
    data_cadastro = database.Column(database.DateTime)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False,
                                          default=1)


class FormasPagamento(database.Model):
    __tablename__ = 'formas_pagamento'
    id = database.Column(database.Integer, primary_key=True)
    nome_forma_pagamento = database.Column(database.String(50), nullable=False)
    id_tipo_transacao = database.Column(database.Integer)
    # 1 - Compra, 2 - Venda, 3 - Compra e Venda
    parcelado = database.Column(database.Integer)
    # 0 - a vista, 1 - parcelado
    situacao = database.Column(database.Integer, default=1)  # 1 - ativo 2 - inativo
    data_cadastro = database.Column(database.DateTime)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False,
                                          default=1)


class TicketsComerciais(database.Model):
    __tablename__ = 'tickets_comerciais'
    id = database.Column(database.Integer, primary_key=True)
    id_tipo_ticket = database.Column(database.Integer)
    # 1 - ticket condicional
    # 2 - ticket compra
    # 3 - ticket venda
    id_ticket_condicional = database.Column(database.Integer)
    id_documento_fiscal = database.Column(database.Integer, database.ForeignKey('documentos_fiscais.id'))
    id_cliente = database.Column(database.Integer, database.ForeignKey('clientes_fornecedores.id'))
    id_fornecedor = database.Column(database.Integer, database.ForeignKey('clientes_fornecedores.id'))
    nro_documento_fiscal = database.Column(database.String(100))
    emissao_documento_fiscal = database.Column(database.DateTime)
    valor_ticket = database.Column(database.Float)
    valor_desconto = database.Column(database.Float)
    valor_acrescimo = database.Column(database.Float)
    valor_final = database.Column(database.Float, default=0)
    parcelas = database.Column(database.Integer, default=1)
    id_forma_pagamento = database.Column(database.Integer, database.ForeignKey('formas_pagamento.id'))
    data_abertura = database.Column(database.DateTime)
    data_chegada = database.Column(database.DateTime)
    data_devolucao = database.Column(database.DateTime)
    data_retirada = database.Column(database.DateTime)
    data_prazo = database.Column(database.DateTime)
    observacoes = database.Column(database.String)
    data_cadastro = database.Column(database.DateTime)
    #  0 - Ticket não finalizado
    #  1 - Em condicional
    #  2 - Extornado
    #  3 - Convertido a compra
    #  4 - Compra não recebida
    #  5 - Compra Recebida
    #  6 - Venda não finalizada
    #  7 - Venda finalizada
    #  8 - Enviado ao Financeiro
    #  9 - Pagamento em Aberto
    # 10 - Pagamento em atraso
    # 11 - Pagamento parcial realizado em atraso
    # 12 - Pagamento parcial realizado
    # 13 - Pagamento realizado em atraso
    # 14 - Pagamento realizado
    # 15 - Cancelado
    # 16 - Devolução parcial
    # 17 - Devolução completa
    # 18 - Finalizado
    situacao = database.Column(database.Integer)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False, default=1)


class StatusTickets(database.Model):
    __tablename__ = 'status_tickets'
    id = database.Column(database.Integer, primary_key=True)
    id_tipo_status = database.Column(database.Integer)
    id_transacao_estoque = database.Column(database.Integer, database.ForeignKey('transacoes_estoque.id'))
    id_transacao_financeira = database.Column(database.Integer, database.ForeignKey('transacoes_financeiras.id'))
    id_ticket_comercial = database.Column(database.Integer, database.ForeignKey('tickets_comerciais.id'))
    status = database.Column(database.Integer)
    situacao = database.Column(database.Integer, default=1)
    data_cadastro = database.Column(database.DateTime, default=func.now())
    id_usuario_cadastro = database.Column(
        database.Integer, 
        database.ForeignKey('usuarios.id', ondelete='CASCADE'), 
        nullable=False
    )


class ItensTicketsComerciais(database.Model):
    __tablename__ = 'itens_tickets_comerciais'
    id = database.Column(database.Integer, primary_key=True)
    id_ticket_comercial = database.Column(database.Integer, database.ForeignKey('tickets_comerciais.id'))
    codigo_item = database.Column(database.String, database.ForeignKey('itens_estoque.codigo_item'))
    valor_item = database.Column(database.Float)
    valor_item_rateio = database.Column(database.Float, default=0)
    qtd = database.Column(database.Float)
    # 0 - Ticket não finalizado
    # 1 - Ativo
    # 2 - Cancelado
    # 3 - Devolvido
    # 4 - Devolvido avariado
    situacao_item_ticket = database.Column(database.Integer)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'))
    data_cadastro = database.Column(database.DateTime)


class TemporariaCompraEstoque(database.Model):
    __tablename__ = 'temporaria_compra_estoque'
    id = database.Column(database.Integer, primary_key=True)
    id_documento_fiscal = database.Column(database.Integer)
    tipo_fornecedor = database.Column(database.Integer)
    pesquisa_fornecedor = database.Column(database.Integer)
    nro_documento_fiscal = database.Column(database.String)
    emissao_documento_fiscal = database.Column(database.DateTime)
    data_chegada = database.Column(database.DateTime)
    data_prazo = database.Column(database.DateTime)
    valor_desconto = database.Column(database.String)
    valor_acrescimo = database.Column(database.String)
    valor_item = database.Column(database.String)
    parcelas = database.Column(database.Integer)
    id_forma_pagamento = database.Column(database.Integer)
    pesquisa_item = database.Column(database.Integer)
    situacao = database.Column(database.Integer)


class FormasParcelamento(database.Model):
    __tablename__ = 'formas_parcelamento'
    id = database.Column(database.Integer, primary_key=True)
    nome_forma_parcelamento = database.Column(database.String(50), nullable=False)
    observacoes = database.Column(database.String(500), nullable=False)
    situacao = database.Column(database.Integer, default=1)  # 1 - ativo 2 - inativo
    data_cadastro = database.Column(database.DateTime)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False,
                                          default=1)


class TransacoesFinanceiras(database.Model):
    __tablename__ = 'transacoes_financeiras'
    id = database.Column(database.Integer, primary_key=True)
    tipo_lancamento = database.Column(database.Integer)
    # 1 - Débito/Crédito Conta Bancaria 2 - Extrato despesa fatura cartao credito, 3 - Receita Cartão de Crédito, 4 - Cheques Terceiros
    lote_transacao = database.Column(database.Integer)
    tipo_transacao = database.Column(database.Integer)
    # 1 - Fluxo de Caixa 2 - Fora Fluxo de caixa 3 - Revisão Financeiro
    id_cheque = database.Column(database.Integer, database.ForeignKey('cheques.id'))
    id_categoria_financeira = database.Column(database.Integer, database.ForeignKey('categorias_financeiras.id'), nullable=False)
    id_conta_bancaria = database.Column(database.Integer, database.ForeignKey('contas_bancarias.id'))
    id_cartao_credito = database.Column(database.Integer, database.ForeignKey('cartao_credito.id'))
    id_fatura_cartao_credito = database.Column(database.Integer, database.ForeignKey('fatura_cartao_credito.id'))
    id_forma_pagamento = database.Column(database.Integer, database.ForeignKey('formas_pagamento.id'))
    id_ticket = database.Column(database.Integer, database.ForeignKey('tickets_comerciais.id'))
    nro_total_parcelas = database.Column(database.Integer)
    nro_parcela_atual = database.Column(database.Integer)
    valor_transacao = database.Column(database.Float, default=0)
    valor_pago = database.Column(database.Float, default=0)
    data_ocorrencia = database.Column(database.DateTime)
    data_pagamento = database.Column(database.DateTime)
    data_vencimento = database.Column(database.DateTime)
    data_cadastro = database.Column(database.DateTime)
    situacao_transacao = database.Column(database.Integer)# 1 - em aberto 2 - vencida 3 - paga 4 - paga em atraso 5 - paga adiantado
    situacao = database.Column(database.Integer, default=1)  # 1 - ativo 2 - inativo
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False,
                                          default=1)


class ValidacaoFaturasCartaoCredito(database.Model):
    __tablename__ = 'validacao_faturas_cartao_credito'
    id = database.Column(database.Integer, primary_key=True)
    id_cartao = database.Column(database.Integer, database.ForeignKey('cartao_credito.id'))
    data_cadastro = database.Column(database.DateTime)


class DocumentosFiscais(database.Model):
    __tablename__ = 'documentos_fiscais'
    id = database.Column(database.Integer, primary_key=True)
    nome_documento = database.Column(database.String(50), nullable=False)
    situacao = database.Column(database.Integer, default=1)  # 1 - ativo 2 - inativo
    data_cadastro = database.Column(database.DateTime)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False,
                                          default=1)


class TipoTicket(database.Model):
    __tablename__ = 'tipo_ticket'
    id = database.Column(database.Integer, primary_key=True)
    nome_tipo_ticket = database.Column(database.String(50), nullable=False)
    situacao = database.Column(database.Integer, default=1)  # 1 - ativo 2 - inativo
    data_cadastro = database.Column(database.DateTime)
    id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False,
                                          default=1)


# TODO: Verificar o que é, documentado no diario de bordo dia 06/08/2024
# class StatusTickets(database.Model):
#     __tablename__ = 'status_tickets'
#     id = database.Column(database.Integer, primary_key=True)
#     # 1 - Movimentação Estoque
#     # 2 - Movimentação Financeiras
#     id_tipo_satus = database.Column(database.Integer)
#     id_transacao_estoque = database.Column(database.Integer, database.ForeignKey('transacoes_estoque.id'))
#     id_transacao_financeira = database.Column(database.Integer, database.ForeignKey('transacoes_financeiras.id'))
#     nome_status = database.Column(database.String(100), nullable=False)
#     quem_atende = database.Column(database.Integer)
#     #1 - Compras 2 - Vendas 3 - Condicionais 4 - Compra&Vendas 5 - Vendas&Condicionas 6 - Compras&Condicionais 7 - Compras&Vendas&Condicionais
#     situacao = database.Column(database.Integer, default=1)  # 1 - ativo 2 - inativo
#     data_cadastro = database.Column(database.DateTime)
#     id_usuario_cadastro = database.Column(database.Integer, database.ForeignKey('usuarios.id'), nullable=False,
#                                           default=1)


class Conferencias(database.Model):
    __tablename__ = 'conferencias'
    id = database.Column(database.Integer, primary_key=True)
    ########### ESTOQUE ###########
    # 1 - data entrada item estoque
    # 2 - data saida item estoque
    # 3 - data entrada e saida item estoque
    # 4 - Qtds itens estoque Todos
    # 5 - Qtd item estoque Individual
    ########## FINANCEIRO ##########
    # 6 - Saldo Conta Todos
    # 7 - Saldo Conta Individual
    # 8 - Atualiza Valor Faturas Todos
    # 9 - Atualiza Valor Faturas Individual
    # 10 - Atualiza Valor Credito Todos
    # 11 - Atualiza Valor Credito Individual
    id_funcao = database.Column(database.Integer)
    id_item = database.Column(database.Integer, database.ForeignKey('itens_estoque.id'))
    id_conta = database.Column(database.Integer, database.ForeignKey('contas_bancarias.id'))
    id_cartao = database.Column(database.Integer, database.ForeignKey('cartao_credito.id'))
    id_fatura = database.Column(database.Integer, database.ForeignKey('fatura_cartao_credito.id'))
    data_cadastro = database.Column(database.DateTime)


class Auditoria(database.Model):
    __tablename__ = 'auditoria'
    id = database.Column(database.Integer, primary_key=True)
    table_name = database.Column(database.String(255), nullable=False)
    operation = database.Column(database.String(50), nullable=False)
    old_data = database.Column(database.JSON)
    new_data = database.Column(database.JSON)
    timestamp = database.Column(database.DateTime, nullable=True)

    def __repr__(self):
        return f"<Auditoria(id={self.id}, table_name='{self.table_name}', operation='{self.operation}', timestamp='{self.timestamp}')>"