from ERP import app, database
from sqlalchemy import text


trigger_data_cadastro = """
    CREATE OR REPLACE FUNCTION atualiza_data_cadastro_function()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.data_cadastro = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
"""


ativar_tg_usuarios = """
    CREATE TRIGGER atualiza_data_cadastro_usuarios
    BEFORE INSERT OR UPDATE ON usuarios
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""


ativar_tg_clientes_fornecedores = """
    CREATE TRIGGER atualiza_data_cadastro_clientes_fornecedores
    BEFORE INSERT OR UPDATE ON clientes_fornecedores
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""


ativar_tg_tipos_cadastro = """
    CREATE TRIGGER atualiza_data_cadastro_tipos_cadastro
    BEFORE INSERT OR UPDATE ON tipos_cadastro
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""


ativar_tg_cadastro_empresa = """
    CREATE TRIGGER atualiza_data_cadastro_cadastro_empresa
    BEFORE INSERT OR UPDATE ON cadastro_empresa
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""


ativar_tg_genero_roupa = """
    CREATE TRIGGER atualiza_data_cadastro_genero_roupa
    BEFORE INSERT OR UPDATE ON genero_roupa
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""


ativar_tg_tipos_roupas = """
    CREATE TRIGGER atualiza_data_cadastro_tipos_roupas
    BEFORE INSERT OR UPDATE ON tipos_roupas
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""


ativar_tg_cores = """
    CREATE TRIGGER atualiza_data_cadastro_cores
    BEFORE INSERT OR UPDATE ON cores
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""


ativar_tg_tamanhos = """
    CREATE TRIGGER atualiza_data_cadastro_tamanhos
    BEFORE INSERT OR UPDATE ON tamanhos
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""


ativar_tg_marcas = """
    CREATE TRIGGER atualiza_data_cadastro_marcas
    BEFORE INSERT OR UPDATE ON marcas
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""


ativar_tg_tipos_unidades = """
    CREATE TRIGGER atualiza_data_cadastro_tipos_unidades
    BEFORE INSERT OR UPDATE ON tipos_unidades
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""


ativar_tg_itens_estoque = """
    CREATE TRIGGER atualiza_data_cadastro_itens_estoque
    BEFORE INSERT OR UPDATE ON itens_estoque
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""


ativar_tg_tipos_transacoes = """
    CREATE TRIGGER atualiza_data_cadastro_tipos_transacoes
    BEFORE INSERT OR UPDATE ON tipos_transacoes
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""


ativar_tg_transacoes_estoque = """
    CREATE TRIGGER atualiza_data_cadastro_transacoes_estoque
    BEFORE INSERT OR UPDATE ON transacoes_estoque
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""


ativar_tg_bancos = """
    CREATE TRIGGER atualiza_data_cadastro_bancos
    BEFORE INSERT OR UPDATE ON bancos
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""


ativar_tg_agencias_bancos = """
    CREATE TRIGGER atualiza_data_cadastro_agencia_bancos
    BEFORE INSERT OR UPDATE ON agencia_bancos
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""


ativar_tg_contas_bancarias = """
    CREATE TRIGGER atualiza_data_cadastro_contas_bancarias
    BEFORE INSERT OR UPDATE ON contas_bancarias
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""


ativar_tg_cartao_credito = """
    CREATE TRIGGER atualiza_data_cadastro_cartao_credito
    BEFORE INSERT OR UPDATE ON cartao_credito
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""


ativar_tg_fatura_cartao_credito = """
    CREATE TRIGGER atualiza_data_cadastro_fatura_cartao_credito
    BEFORE INSERT OR UPDATE ON fatura_cartao_credito
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""


ativar_tg_categorias_financeiras = """
CREATE TRIGGER atualiza_data_cadastro_categorias_financeiras
BEFORE INSERT OR UPDATE ON categorias_financeiras
FOR EACH ROW
EXECUTE FUNCTION atualiza_data_cadastro_function();
"""

class Gatilhos:


    def __init__(self):
        self.app = app
        self.database = database


    def cria_gatilho_data_cadastro(self):
        with self.app.app_context():
            self.database.session.execute(text(trigger_data_cadastro))
            self.database.session.commit()

    def cria_gatilhos_tabelas(self):
        # Lista de gatilhos a serem criados
        gatilhos = [
            ativar_tg_usuarios, ativar_tg_clientes_fornecedores, ativar_tg_tipos_cadastro,
            ativar_tg_cadastro_empresa, ativar_tg_genero_roupa, ativar_tg_tipos_roupas,
            ativar_tg_cores, ativar_tg_tamanhos, ativar_tg_marcas, ativar_tg_tipos_unidades,
            ativar_tg_itens_estoque, ativar_tg_tipos_transacoes, ativar_tg_transacoes_estoque,
            ativar_tg_bancos, ativar_tg_agencias_bancos, ativar_tg_contas_bancarias,
            ativar_tg_cartao_credito, ativar_tg_fatura_cartao_credito, ativar_tg_categorias_financeiras
        ]

        # Executar cada gatilho na lista
        with self.app.app_context():
            for gatilho in gatilhos:
                statement = text(gatilho)
                self.database.session.execute(statement)
                self.database.session.commit()