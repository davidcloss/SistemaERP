from ERP.routes import busca_ultima_transacao_estoque
from ERP.models import TiposTransacoesEstoque
from ERP import app, database


with app.app_context():
    retorno = TiposTransacoesEstoque.query.filter_by(nome_tipo_transacao='Entrada').first()
    print(retorno.id)