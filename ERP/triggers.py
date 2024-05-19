from ERP import app, database
from sqlalchemy import text

# 1 - DATA CADASTRO


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


# 2 - DATA ULTIMA ENTRADA ITEM ESTOQUE = TRANSACAO POSITIVA


trigger_data_ultima_entrada_transacoes = """
    CREATE OR REPLACE FUNCTION atualiza_data_ultima_entrada_transacoes()
    RETURNS TRIGGER AS $$
    BEGIN
        IF NEW.tipo_transacao IN (1, 3, 5) THEN
            UPDATE itens_estoque
            SET data_ultima_entrada = NEW.data_transacao
            WHERE id = NEW.id_item;
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
"""


ativar_tg_data_ultima_entrada_transacoes = """
    CREATE TRIGGER trg_after_insert_update_transacoes_estoque_entrada
    BEFORE INSERT OR UPDATE ON transacoes_estoque
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_ultima_entrada_transacoes();
"""


# 2 - DATA ULTIMA SAIDA ITEM ESTOQUE = TRANSACAO POSITIVA


trigger_data_ultima_saida_transacoes = """
    CREATE OR REPLACE FUNCTION atualiza_data_ultima_saida_transacoes()
    RETURNS TRIGGER AS $$
    BEGIN
        IF NEW.tipo_transacao IN (2, 4, 6) THEN
            UPDATE itens_estoque
            SET data_ultima_saida = NEW.data_transacao
            WHERE id = NEW.id_item;
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
"""


ativar_tg_data_ultima_saida_transacoes = """
    CREATE TRIGGER trg_after_insert_update_transacoes_estoque_saida
    BEFORE INSERT OR UPDATE ON transacoes_estoque
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_ultima_saida_transacoes();
"""



# 3 QTD TABELA ITENS_ESTOQUE TODA VEZ QUE ATUALIZA TRANSACOES_ESTOQUE ENTRADA




trigger_atualiza_qtd_estoque_entrada = """
CREATE OR REPLACE FUNCTION atualiza_quantidade_estoque()
RETURNS TRIGGER AS $$
DECLARE
    entradas FLOAT;
    saidas FLOAT;
    custo_entradas FLOAT := 0;
    custo_saidas FLOAT := 0;
    qtd_final FLOAT;
    custo_final FLOAT;
    valor_unitario_venda_itens_estoque FLOAT;
BEGIN
    -- Calcular as entradas
    SELECT COALESCE(SUM(qtd_transacao), 0)
    INTO entradas
    FROM transacoes_estoque
    WHERE id_item = NEW.id_item
    AND tipo_transacao IN (1, 3, 5);
    
    -- Calcular os custos de entradas
    SELECT COALESCE(SUM(valor_total_transacao_custo), 0)
    INTO custo_entradas
    FROM transacoes_estoque
    WHERE id_item = NEW.id_item
    AND tipo_transacao IN (1, 3, 5);

    -- Calcular as saídas
    SELECT COALESCE(SUM(qtd_transacao), 0)
    INTO saidas
    FROM transacoes_estoque
    WHERE id_item = NEW.id_item
    AND tipo_transacao IN (2, 4, 6);
    
    -- Calcular os custos de saídas
    SELECT COALESCE(SUM(valor_total_transacao_custo), 0)
    INTO custo_saidas
    FROM transacoes_estoque
    WHERE id_item = NEW.id_item
    AND tipo_transacao IN (2, 4, 6);

    -- Calcular a quantidade final e o custo final
    qtd_final := COALESCE(entradas - saidas, 0);
    custo_final := COALESCE(custo_entradas - custo_saidas, 0);

    -- Obter o valor unitário de venda
    SELECT valor_unitario_venda
    INTO valor_unitario_venda_itens_estoque
    FROM itens_estoque
    WHERE id = NEW.id_item;

    -- Atualizar a quantidade na tabela itens_estoque
    UPDATE itens_estoque
    SET 
        qtd = qtd_final,
        valor_estoque_custo = custo_final,
        valor_unitario_medio_custo = CASE 
            WHEN qtd_final = 0 THEN 0
            ELSE custo_final / qtd_final
        END,
        valor_estoque_venda = COALESCE(qtd_final * valor_unitario_venda_itens_estoque, 0)
    WHERE id = NEW.id_item;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""


ativar_tg_atualiza_qtd_estoque_entrada = """
    CREATE TRIGGER trg_after_insert_transacoes_estoque_qtd
    AFTER INSERT OR UPDATE ON transacoes_estoque
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_quantidade_estoque();
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


    def ativa_gatilho_data_ultima_entrada_item_estoque(self):
        with self.app.app_context():
            self.database.session.execute(text(ativar_tg_data_ultima_entrada_transacoes))
            self.database.session.commit()


    def cria_gatilho_data_ultima_entrada_item_estoque(self):
        with self.app.app_context():
            self.database.session.execute(text(trigger_data_ultima_entrada_transacoes))
            self.database.session.commit()
        self.ativa_gatilho_data_ultima_entrada_item_estoque()


    def ativa_gatilho_data_ultima_saida_item_estoque(self):
        with self.app.app_context():
            self.database.session.execute(text(ativar_tg_data_ultima_saida_transacoes))
            self.database.session.commit()


    def cria_gatilho_data_ultima_saida_item_estoque(self):
        with self.app.app_context():
            self.database.session.execute(text(trigger_data_ultima_saida_transacoes))
            self.database.session.commit()
        self.ativa_gatilho_data_ultima_saida_item_estoque()


    def ativa_gatilho_qtd_estoque_entrada(self):
        with self.app.app_context():
            self.database.session.execute(text(ativar_tg_atualiza_qtd_estoque_entrada))
            self.database.session.commit()


    def cria_gatilho_atualiza_qtd_estoque_entrada(self):
        with self.app.app_context():
            self.database.session.execute(text(trigger_atualiza_qtd_estoque_entrada))
            self.database.session.commit()
        self.ativa_gatilho_qtd_estoque_entrada()


    def triggers_tabela_item_estoque(self):
        self.cria_gatilho_data_ultima_entrada_item_estoque()
        self.cria_gatilho_data_ultima_saida_item_estoque()
        self.cria_gatilho_atualiza_qtd_estoque_entrada()
