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

ativar_tg_formas_pagamento = """
    CREATE TRIGGER atualiza_data_cadastro_formas_pagamento
    BEFORE INSERT OR UPDATE ON formas_pagamento
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""

ativar_tg_transacoes_financeiras = """
    CREATE TRIGGER atualiza_data_cadastro_transacoes_financeiras
    BEFORE INSERT OR UPDATE ON transacoes_financeiras
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""

ativar_tg_documentos_fiscais = """
    CREATE TRIGGER atualiza_data_cadastro_documentos_fiscais
    BEFORE INSERT OR UPDATE ON documentos_fiscais
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""

ativar_tg_tipo_ticket = """
    CREATE TRIGGER atualiza_data_cadastro_tipo_ticket
    BEFORE INSERT OR UPDATE ON tipo_ticket
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""

ativar_tg_status_tickets = """
    CREATE TRIGGER atualiza_data_cadastro_status_tickets
    BEFORE INSERT OR UPDATE ON status_tickets
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""

ativar_tg_tickets_comerciais = """
    CREATE TRIGGER atualiza_data_cadastro_tickets_comerciais
    BEFORE INSERT OR UPDATE ON tickets_comerciais
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""

ativar_tg_validacao_faturas_cartao_credito = """
    CREATE TRIGGER atualiza_data_cadastro_validacao_faturas_cartao_credito
    BEFORE INSERT OR UPDATE ON validacao_faturas_cartao_credito
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""


ativar_tg_conferencias = """
    CREATE TRIGGER atualiza_data_cadastro_conferencias
    BEFORE INSERT OR UPDATE ON conferencias
    FOR EACH ROW
    EXECUTE FUNCTION atualiza_data_cadastro_function();
"""
####
trigger_sync_fatura_carta_credito_transacoes_financeiras = """
    -- Criação da função que será chamada pelo trigger
    CREATE OR REPLACE FUNCTION sync_transacoes_financeiras()
    RETURNS TRIGGER AS $$
    DECLARE
    last_lote_transacao INTEGER;
    id_conta_bancaria_id INTEGER;
    BEGIN
         -- Obtém o valor de id_conta_bancaria da tabela cartao_credito
        SELECT id_conta_bancaria 
        INTO id_conta_bancaria_id
        FROM cartao_credito 
        WHERE id = NEW.id_cartao_credito;
        -- Verifica se existe uma transação financeira com o id_fatura_cartao_credito e tipo_transacao = 1
        IF EXISTS (SELECT 1 FROM transacoes_financeiras 
                   WHERE id_fatura_cartao_credito = NEW.id 
                     AND tipo_transacao = 1) THEN
            -- Atualiza a transação financeira existente
            UPDATE transacoes_financeiras
        SET data_vencimento = NEW.data_vcto,
            tipo_lancamento = 2,
            id_usuario_cadastro = NEW.id_usuario_cadastro,
            valor_pago = NEW.valor_pago,
            valor_transacao = NEW.valor_fatura,
            id_cartao_credito = NEW.id_cartao_credito,
            data_pagamento = NEW.data_pagamento,
            id_conta_bancaria = id_conta_bancaria_id
        WHERE id_fatura_cartao_credito = NEW.id
          AND tipo_transacao = 1;
        ELSE
            -- Obtém o último valor do campo lote_transacao
        SELECT COALESCE(MAX(lote_transacao), 0) INTO last_lote_transacao FROM transacoes_financeiras;

        -- Cria uma nova transação financeira
        INSERT INTO transacoes_financeiras (
            tipo_transacao, 
            tipo_lancamento,
            id_categoria_financeira, 
            id_fatura_cartao_credito, 
            data_vencimento, 
            id_usuario_cadastro,
            lote_transacao,
            valor_pago,
            valor_transacao,
            id_cartao_credito,
            data_pagamento,
            id_conta_bancaria,
            id_forma_pagamento,
            situacao_transacao,
            situacao,
            data_ocorrencia
        ) VALUES (
            1, 
            2,
            2, 
            NEW.id, 
            NEW.data_vcto,
            NEW.id_usuario_cadastro,
            last_lote_transacao + 1,
            0,
            NEW.valor_fatura,
            NEW.id_cartao_credito,
            NEW.data_pagamento,
            id_conta_bancaria_id,
            1,
            1,
            1,
            NEW.data_vcto
        );
    END IF;

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
"""


ativar_tg_sync_fatura_carta_credito_transacoes_financeiras = """
    CREATE TRIGGER trigger_sync_transacoes_financeiras
    AFTER INSERT OR UPDATE ON fatura_cartao_credito
    FOR EACH ROW
    EXECUTE FUNCTION sync_transacoes_financeiras();
"""

trigger_atualiza_valor_fatura_cartao_credito = """
    CREATE OR REPLACE FUNCTION atualizar_valor_fatura_cartao_credito()
    RETURNS TRIGGER AS $$
    DECLARE
        gastos NUMERIC;
        abatimentos NUMERIC;
    BEGIN
        -- Verifica se o tipo de transação é 2 e se id_fatura_cartao_credito não é nulo
        IF NEW.tipo_lancamento = 2 THEN
            -- Calcula o total de gastos
            SELECT SUM(tf.valor_transacao) INTO gastos
            FROM transacoes_financeiras tf
            JOIN categorias_financeiras cf ON tf.id_categoria_financeira = cf.id
            WHERE tf.id_fatura_cartao_credito = NEW.id_fatura_cartao_credito
              AND cf.tipo_transacao_financeira IN (2, 3, 5);

            -- Calcula o total de abatimentos
            SELECT SUM(tf.valor_transacao) INTO abatimentos
            FROM transacoes_financeiras tf
            JOIN categorias_financeiras cf ON tf.id_categoria_financeira = cf.id
            WHERE tf.id_fatura_cartao_credito = NEW.id_fatura_cartao_credito
              AND cf.tipo_transacao_financeira IN (1, 4);

            -- Atualiza o valor da fatura
            UPDATE fatura_cartao_credito
            SET valor_fatura = COALESCE(gastos, 0) - COALESCE(abatimentos, 0)
            WHERE id = NEW.id_fatura_cartao_credito;
        END IF;

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
"""

ativar_tg_atualiza_valor_fatura_cartao_credito = """
    CREATE TRIGGER trigger_atualizar_valor_fatura_cartao_credito
    AFTER INSERT OR UPDATE ON transacoes_financeiras
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_valor_fatura_cartao_credito();
"""
trigger_atualiza_valor_gasto_cartao_credito = """
    CREATE OR REPLACE FUNCTION atualizar_valor_gasto_cartao_credito()
    RETURNS TRIGGER AS $$
    DECLARE
        valor_limite_total NUMERIC;
        valor_utilizado NUMERIC;
    BEGIN
        -- Busca o valor_limite_total do cartao_credito
        SELECT c.valor_limite INTO valor_limite_total
        FROM cartao_credito c
        WHERE c.id = NEW.id_cartao_credito;

        -- Calcula a soma de todas as faturas com situacao_fatura igual a 0 ou 2
        

        -- Atualiza as colunas valor_utilizado e valor_disponivel no cartao_credito
        UPDATE cartao_credito
        SET valor_gasto = COALESCE(valor_utilizado, 0),
            valor_disponivel = valor_limite_total - COALESCE(valor_utilizado, 0)
        WHERE id = NEW.id_cartao_credito;

        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
"""

ativar_tg_trigger_atualiza_valor_gasto_cartao_credito = """
    CREATE TRIGGER trigger_atualizar_valor_gasto_cartao_credito
    AFTER INSERT OR UPDATE ON fatura_cartao_credito
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_valor_gasto_cartao_credito();
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
            ativar_tg_cartao_credito, ativar_tg_fatura_cartao_credito, ativar_tg_categorias_financeiras,
            ativar_tg_formas_pagamento, ativar_tg_transacoes_financeiras, ativar_tg_documentos_fiscais,
            ativar_tg_tipo_ticket, ativar_tg_status_tickets, ativar_tg_tickets_comerciais,
            ativar_tg_validacao_faturas_cartao_credito, ativar_tg_conferencias]

        # Executar cada gatilho na lista
        with self.app.app_context():
            for gatilho in gatilhos:
                statement = text(gatilho)
                self.database.session.execute(statement)
                self.database.session.commit()
    #
    # def ativa_gatilho_data_ultima_entrada_item_estoque(self):
    #     with self.app.app_context():
    #         self.database.session.execute(text(ativar_tg_data_ultima_entrada_transacoes))
    #         self.database.session.commit()
    #
    # def cria_gatilho_data_ultima_entrada_item_estoque(self):
    #     with self.app.app_context():
    #         self.database.session.execute(text(trigger_data_ultima_entrada_transacoes))
    #         self.database.session.commit()
    #     self.ativa_gatilho_data_ultima_entrada_item_estoque()
    #
    # def ativa_gatilho_data_ultima_saida_item_estoque(self):
    #     with self.app.app_context():
    #         self.database.session.execute(text(ativar_tg_data_ultima_saida_transacoes))
    #         self.database.session.commit()
    #
    # def cria_gatilho_data_ultima_saida_item_estoque(self):
    #     with self.app.app_context():
    #         self.database.session.execute(text(trigger_data_ultima_saida_transacoes))
    #         self.database.session.commit()
    #     self.ativa_gatilho_data_ultima_saida_item_estoque()
    #
    # def ativa_gatilho_qtd_estoque_entrada(self):
    #     with self.app.app_context():
    #         self.database.session.execute(text(ativar_tg_atualiza_qtd_estoque_entrada))
    #         self.database.session.commit()
    #
    # def cria_gatilho_atualiza_qtd_estoque_entrada(self):
    #     with self.app.app_context():
    #         self.database.session.execute(text(trigger_atualiza_qtd_estoque_entrada))
    #         self.database.session.commit()
    #     self.ativa_gatilho_qtd_estoque_entrada()
    #
    # def triggers_tabela_item_estoque(self):
    #     self.cria_gatilho_data_ultima_entrada_item_estoque()
    #     self.cria_gatilho_data_ultima_saida_item_estoque()
    #     self.cria_gatilho_atualiza_qtd_estoque_entrada()
    #
    # def ativa_gatilho_saldo_conta_bancaria(self):
    #     with self.app.app_context():
    #         self.database.session.execute(text(ativar_tg_atualiza_saldo_conta_bancaria))
    #         self.database.session.commit()
    #
    # def cria_gatilho_atualiza_saldo_conta_bancaria(self):
    #     with self.app.app_context():
    #         self.database.session.execute(text(trigger_atualiza_saldo_conta_bancaria))
    #         self.database.session.commit()
    #     self.ativa_gatilho_saldo_conta_bancaria()
    #
    # def ativa_gatilho_atualiza_cheque_especial(self):
    #     with app.app_context():
    #         self.database.session.execute(text(ativar_tg_atualiza_cheque_especial))
    #         self.database.session.commit()
    #
    # def cria_gatilho_atualiza_cheque_especial(self):
    #     with self.app.app_context():
    #         self.database.session.execute(text(trigger_atualiza_cheque_especial))
    #         self.database.session.commit()
    #     self.ativa_gatilho_atualiza_cheque_especial()
    #
    # def ativa_gatilho_sync_fatura_cartao_credito_transacoes_financeiras(self):
    #     with self.app.app_context():
    #         self.database.session.execute(text(ativar_tg_sync_fatura_carta_credito_transacoes_financeiras))
    #         self.database.session.commit()
    #
    # def cria_gatilho_sync_fatura_cartao_credito_transacoes_financeiras(self):
    #     with self.app.app_context():
    #         self.database.session.execute(text(trigger_sync_fatura_carta_credito_transacoes_financeiras))
    #         self.database.session.commit()
    #     self.ativa_gatilho_sync_fatura_cartao_credito_transacoes_financeiras()
    #
    # def ativa_gatilho_atualiza_valor_fatura_cartao_credito(self):
    #     with self.app.app_context():
    #         self.database.session.execute(text(ativar_tg_atualiza_valor_fatura_cartao_credito))
    #         self.database.session.commit()
    #
    # def cria_gatilho_atualiza_valor_fatura_cartao_credito(self):
    #     with self.app.app_context():
    #         self.database.session.execute(text(trigger_atualiza_valor_fatura_cartao_credito))
    #         self.database.session.commit()
    #     self.ativa_gatilho_atualiza_valor_fatura_cartao_credito()
    #
    # def ativa_gatilho_atualiza_valor_gasto_cartao_credito(self):
    #     with self.app.app_context():
    #         self.database.session.execute(text(ativar_tg_trigger_atualiza_valor_gasto_cartao_credito))
    #         self.database.session.commit()
    #
    # def cria_gatilho_atualiza_valor_gasto_cartao_credito(self):
    #     with self.app.app_context():
    #         self.database.session.execute(text(trigger_atualiza_valor_gasto_cartao_credito))
    #         self.database.session.commit()
    #     self.ativa_gatilho_atualiza_valor_gasto_cartao_credito()
    #
    # def triggers_financeiro(self):
    #     self.cria_gatilho_atualiza_saldo_conta_bancaria()
    #     self.cria_gatilho_atualiza_cheque_especial()
    #     self.cria_gatilho_sync_fatura_cartao_credito_transacoes_financeiras()
    #     self.cria_gatilho_atualiza_valor_fatura_cartao_credito()
    #     self.cria_gatilho_atualiza_valor_gasto_cartao_credito()