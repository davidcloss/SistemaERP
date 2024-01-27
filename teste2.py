from ERP.routes import busca_ultima_transacao_estoque
from ERP.models import TiposTransacoesEstoque
from ERP import app, database
from ERP.routes import gera_faturas_cartao


with app.app_context():
    gera_faturas_cartao()