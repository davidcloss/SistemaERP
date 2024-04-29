from ERP import database, app
from sqlalchemy import text
from ERP.models import Usuarios, SituacoesUsuarios, ClientesFornecedores, TiposCadastros, TiposUsuarios, \
                       CadastroEmpresa, GeneroRoupa, TiposRoupas, Cores, Tamanhos, Marcas, TiposUnidades, \
                       ItensEstoque, TiposTransacoesEstoque, TransacoesEstoque, Bancos, AgenciaBanco, \
                       ContasBancarias, CartaoCredito, FaturaCartaoCredito, CategoriasFinanceiras



def create_audit_trigger(model_class):
    table_name = model_class.__table__.name
    trigger_name = f'audit_trigger_{table_name}'
    function_name = 'audit_function'

    # Verificar se o gatilho já existe para a tabela
    trigger_exists = database.session.execute(
        text("SELECT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = :trigger_name)"),
        {"trigger_name": trigger_name}
    ).scalar()

    # Se o gatilho não existir, criar um novo
    if not trigger_exists:
        database.session.execute(
            text(f"CREATE OR REPLACE FUNCTION {function_name}() RETURNS TRIGGER AS $$\n"
                 f"BEGIN\n"
                 f"    IF (TG_OP = 'UPDATE') THEN\n"
                 f"        INSERT INTO auditoria (table_name, operation, old_data, new_data, \"timestamp\")\n"
                 f"        VALUES (TG_TABLE_NAME, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW), current_timestamp);\n"
                 f"    ELSIF (TG_OP = 'INSERT') THEN\n"
                 f"        INSERT INTO auditoria (table_name, operation, new_data, \"timestamp\")\n"
                 f"        VALUES (TG_TABLE_NAME, 'INSERT', to_jsonb(NEW), current_timestamp);\n"
                 f"    ELSIF (TG_OP = 'DELETE') THEN\n"
                 f"        INSERT INTO auditoria (table_name, operation, old_data, \"timestamp\")\n"
                 f"        VALUES (TG_TABLE_NAME, 'DELETE', to_jsonb(OLD), current_timestamp);\n"
                 f"    END IF;\n"
                 f"    RETURN NULL;\n"
                 f"END;\n"
                 f"$$ LANGUAGE plpgsql;\n"
                 f"CREATE TRIGGER {trigger_name}\n"
                 f"AFTER INSERT OR UPDATE OR DELETE ON {table_name}\n"
                 f"FOR EACH ROW EXECUTE FUNCTION {function_name}()")
        )
        database.session.commit()
        print(f"Gatilho de auditoria criado com sucesso para a tabela {table_name}.")
    else:
        print(f"O gatilho de auditoria para a tabela {table_name} já existe.")

tabelas = [Usuarios, SituacoesUsuarios, ClientesFornecedores, TiposCadastros, TiposUsuarios, \
                       CadastroEmpresa, GeneroRoupa, TiposRoupas, Cores, Tamanhos, Marcas, TiposUnidades, \
                       ItensEstoque, TiposTransacoesEstoque, TransacoesEstoque, Bancos, AgenciaBanco, \
                       ContasBancarias, CartaoCredito, FaturaCartaoCredito, CategoriasFinanceiras]

# Chamar a função para cada modelo
with app.app_context():
    for tab in tabelas:
        create_audit_trigger(tab)