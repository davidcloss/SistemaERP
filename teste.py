from ERP import app, database
from ERP.models import TiposCadastros
from datetime import datetime
import sqlite3 as sql


def criar_deletar_db(cod):
    if cod == 1:
        with app.app_context():
            database.create_all()
    elif cod == 2:
        with app.app_context():
            database.drop_all()

criar_deletar_db(2)
criar_deletar_db(1)



lista_tipos_cadastro = ['Cliente', 'Fornecedor', 'Cliente/Fornecedor', 'Empresa Própria']

with app.app_context():
    for tipo in lista_tipos_cadastro:
        tipos_cadastros = TiposCadastros(nome_tipo=tipo)
        database.session.add(tipos_cadastros)
        database.session.commit()

with app.app_context():
    retorno = TiposCadastros.query.all()
    print(retorno)


print(datetime.utcnow().date())