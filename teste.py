from ERP import app, database, bcrypt
from ERP.models import GeneroRoupa
from ERP.triggers import Gatilhos
from datetime import datetime
from ERP.logs_auditoria import create_audit_trigger
from ERP.models import Usuarios, SituacoesUsuarios, ClientesFornecedores, TiposCadastros, TiposUsuarios, \
                       CadastroEmpresa, GeneroRoupa, TiposRoupas, Cores, Tamanhos, Marcas, TiposUnidades, \
                       ItensEstoque, TiposTransacoesEstoque, TransacoesEstoque, Bancos, AgenciaBanco, \
                       ContasBancarias, CartaoCredito, FaturaCartaoCredito, CategoriasFinanceiras


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
           ContasBancarias, CartaoCredito, FaturaCartaoCredito, CategoriasFinanceiras]

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

tipos_transacoes = ['Entrada', 'Saída', 'Ajuste Estoque +', 'Ajuste Estoque -']
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

print(datetime.utcnow().date())