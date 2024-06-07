from ERP import app, database, bcrypt
from ERP.triggers import Gatilhos
from datetime import datetime
from ERP.logs_auditoria import create_audit_trigger
from ERP.models import Usuarios, SituacoesUsuarios, ClientesFornecedores, TiposCadastros, TiposUsuarios, \
                       CadastroEmpresa, GeneroRoupa, TiposRoupas, Cores, Tamanhos, Marcas, TiposUnidades, \
                       ItensEstoque, TiposTransacoesEstoque, TransacoesEstoque, Bancos, AgenciaBanco, \
                       ContasBancarias, CartaoCredito, FaturaCartaoCredito, CategoriasFinanceiras, \
                       TipoTicket, FormasPagamento, TransacoesFinanceiras, DocumentosFiscais, \
                       StatusTickets, TicketsComerciais, ValidacaoFaturasCartaoCredito


def criar_deletar_db(cod):
    if cod == 1:
        with app.app_context():
            database.create_all()
    elif cod == 2:
        with app.app_context():
            database.drop_all()


criar_deletar_db(2)
criar_deletar_db(1)


gatilhos = Gatilhos()
gatilhos.cria_gatilho_data_cadastro()
gatilhos.cria_gatilhos_tabelas()


tabelas = [Usuarios, SituacoesUsuarios, ClientesFornecedores, TiposCadastros, TiposUsuarios, \
           CadastroEmpresa, GeneroRoupa, TiposRoupas, Cores, Tamanhos, Marcas, TiposUnidades, \
           ItensEstoque, TiposTransacoesEstoque, TransacoesEstoque, Bancos, AgenciaBanco, \
           ContasBancarias, CartaoCredito, FaturaCartaoCredito, CategoriasFinanceiras, \
           TipoTicket, FormasPagamento, TransacoesFinanceiras, DocumentosFiscais, \
           StatusTickets, TicketsComerciais, ValidacaoFaturasCartaoCredito]


# Chamar a função para cada modelo
with app.app_context():
    for tab in tabelas:
        create_audit_trigger(tab)


sit = ['Ativo', 'Inativo']
with app.app_context():
    for s in sit:
        situacao = SituacoesUsuarios(nome_situacao=s)
        database.session.add(situacao)
        database.session.commit()


tipos_usuario = ['Gerente', 'Financeiro(a)', 'Vendedor(a)', 'Administrador(a)', 'Supervisor(a)', 'Coordenador(a)']
with app.app_context():
    for tipo in tipos_usuario:
        tipo_usu = TiposUsuarios(nome_tipo=tipo)
        database.session.add(tipo_usu)
        database.session.commit()


with app.app_context():
    senha = '1234567890'
    senha_hash = bcrypt.generate_password_hash(senha).decode('UTF-8')
    usuario = Usuarios(username='GERENTE',
                       senha=senha_hash,
                       tipo_usuario=1)
    database.session.add(usuario)
    database.session.commit()


cores = ['Laranja', 'Vermelho', 'Azul']
with app.app_context():
    for cor in cores:
        c = Cores(nome_cor=cor)
        database.session.add(c)
        database.session.commit()
with app.app_context():
    retorno = TiposCadastros.query.all()
    print(retorno)


lista_tipos_cadastro = ['Cliente', 'Fornecedor', 'Cliente/Fornecedor', 'Empresa Própria']


with app.app_context():
    for tipo in lista_tipos_cadastro:
        tipos_cadastros = TiposCadastros(nome_tipo=tipo)
        database.session.add(tipos_cadastros)
        database.session.commit()


tipos_roupas = ['Calça', 'Camiseta', 'Jaqueta']
with app.app_context():
    for tipo in tipos_roupas:
        t = TiposRoupas(nome_tipo_roupa=tipo)
        database.session.add(t)
        database.session.commit()


marcas = ['Mamô', 'Gardana', 'Biamar']
with app.app_context():
    for mar in marcas:
        m = Marcas(nome_marca=mar)
        database.session.add(m)
        database.session.commit()


tamanhos = ['P', 'M', 'G', 'GG']
with app.app_context():
    for tam in tamanhos:
        t = Tamanhos(nome_tamanho=tam)
        database.session.add(t)
        database.session.commit()


tipos_transacoes = ['Entrada', 'Saída', 'Transferência +', 'Transferência -', 'Devolução +', 'Devolução -', 'Ajuste Estoque +', 'Ajuste Estoque -',  'Condicional +', 'Condicional -']
with app.app_context():
    for tipo in tipos_transacoes:
        t = TiposTransacoesEstoque(nome_tipo_transacao=tipo)
        database.session.add(t)
        database.session.commit()


tipos_unidades = ['Unidade', 'Metro', 'Centimetro +', 'Kilos', 'Gramas']
with app.app_context():
    for tipo in tipos_unidades:
        t = TiposUnidades(nome_tipo_unidade=tipo)
        database.session.add(t)
        database.session.commit()


tipos_generos = ['Masculino', 'Feminino', 'Unissex']
with app.app_context():
    for tipo in tipos_generos:
        t = GeneroRoupa(nome_genero=tipo)
        database.session.add(t)
        database.session.commit()


gatilhos.triggers_financeiro()

with app.app_context():
    fornecedor = ClientesFornecedores(nome_fantasia='Mimos', razao_social='Mimos LTDA',
                                      cnpj='12345678901234', rua='Rua do Centro',
                                      complemento='Loja 1', nro='201', bairro='Centro',
                                      cidade='Garibaldi', uf='RS', cep='95720000',
                                      data_fundacao=datetime.strptime('01/01/2002', '%d/%m/%Y'),
                                      telefone='1234567890', email='teste@gmail.com',
                                      tipo_cadastro=4, id_usuario_cadastro=1)
    database.session.add(fornecedor)
    database.session.commit()


with app.app_context():
    fornecedor = ClientesFornecedores(nome_fantasia='Banco', razao_social='Banco LTDA',
                                      cnpj='01234567890123', rua='Rua do Centro',
                                      complemento='Sala Térreo', nro='6001', bairro='Centro',
                                      cidade='Garibaldi', uf='RS', cep='95720000',
                                      data_fundacao=datetime.strptime('01/01/1950', '%d/%m/%Y'),
                                      telefone='12345678910', email='teste@banco.com',
                                      tipo_cadastro=2, id_usuario_cadastro=1)
    database.session.add(fornecedor)
    database.session.commit()


categorias = [('Saldo Inicial Conta', 1), ('Fatura Cartão Crédito', 0), ('Descontos Recebidos', 1), ('Multas por atraso recebidas', 3)]
with app.app_context():
    for categoria in categorias:
        cat = CategoriasFinanceiras(nome_categoria=categoria[0],
                                    tipo_transacao_financeira=categoria[1])
        database.session.add(cat)
        database.session.commit()


formas_pagamento = ['À vista']
with app.app_context():
    for forma in formas_pagamento:
        f = FormasPagamento(nome_forma_pagamento=forma)
        database.session.add(f)
        database.session.commit()



bancos = [(1, 'Banco do Brasil'), (41, 'Banrisul'), (750, 'Sicredi'), (756, 'Sicoob')]
with app.app_context():
    for banco in bancos:
        b = Bancos(cod_banco=banco[0],
                   nome_banco=banco[1])
        database.session.add(b)
        database.session.commit()


agencia = {'agencia': '765', 'digito_agencia': '1', 'id_banco': 1, 'apelido_agencia': 'Teste-Agencia', 'id_cliente': 2}
with app.app_context():
    a = AgenciaBanco(agencia=agencia['agencia'],
                     digito_agencia=agencia['digito_agencia'],
                     id_banco=agencia['id_banco'],
                     apelido_agencia=agencia['apelido_agencia'],
                     id_cliente=agencia['id_cliente'])
    database.session.add(a)
    database.session.commit()


with app.app_context():
    conta = ContasBancarias(id_agencia=1, apelido_conta='Teste Conta',
                            nro_conta='1789', digito_conta='2',
                            id_titular=1, cheque_especial=5000)
    database.session.add(conta)
    database.session.commit()
    transacao = TransacoesFinanceiras(id_categoria_financeira=1,
                                      lote_transacao=1,
                                      tipo_transacao=1,
                                      id_conta_bancaria=1,
                                      valor_transacao=-500,
                                      data_pagamento=datetime.now(),
                                      situacao_transacao=3)
    database.session.add(transacao)
    database.session.commit()

gatilhos.triggers_tabela_item_estoque()


print(datetime.utcnow().date())