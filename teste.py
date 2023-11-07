from ERP import app, database
from datetime import datetime


def criar_deletar_db(cod):
    if cod == 1:
        with app.app_context():
            database.create_all()
    elif cod == 2:
        with app.app_context():
            database.drop_all()

criar_deletar_db(2)
criar_deletar_db(1)

print(datetime.utcnow().date())