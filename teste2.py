from sqlalchemy.orm import sessionmaker
from sqlalchemy import text


def excluir_todas_as_triggers():
    # Obtém a sessão do banco de dados
    session = db.session

    # Consulta para obter todas as triggers
    consulta_obter_triggers = """
    SELECT tgname, relname
    FROM pg_trigger
    JOIN pg_class ON pg_trigger.tgrelid = pg_class.oid
    WHERE NOT tgisinternal;
    """

    # Executa a consulta para obter os nomes das triggers e das tabelas
    resultados = session.execute(text(consulta_obter_triggers)).fetchall()

    # Gera e executa os comandos para excluir as triggers
    for trigger in resultados:
        nome_trigger = trigger[0]
        nome_tabela = trigger[1]
        comando_excluir_trigger = f"DROP TRIGGER IF EXISTS {nome_trigger} ON {nome_tabela};"
        session.execute(text(comando_excluir_trigger))

    session.commit()
    print("Todas as triggers foram excluídas com sucesso.")
