-- 1 trigger data_cadastro
-- 1.1 Função
CREATE OR REPLACE FUNCTION atualiza_data_cadastro_function()
RETURNS TRIGGER AS $$
BEGIN
    NEW.data_cadastro = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 1.2 triggers por tabela

CREATE TRIGGER atualiza_data_cadastro_usuarios
BEFORE INSERT OR UPDATE ON usuarios
FOR EACH ROW
EXECUTE FUNCTION atualiza_data_cadastro_function();

CREATE TRIGGER atualiza_data_cadastro_clientes_fornecedores
BEFORE INSERT OR UPDATE ON clientes_fornecedores
FOR EACH ROW
EXECUTE FUNCTION atualiza_data_cadastro_function();

CREATE TRIGGER atualiza_data_cadastro_tipos_cadastro
BEFORE INSERT OR UPDATE ON tipos_cadastro
FOR EACH ROW
EXECUTE FUNCTION atualiza_data_cadastro_function();

CREATE TRIGGER atualiza_data_cadastro_cadastro_empresa
BEFORE INSERT OR UPDATE ON cadastro_empresa
FOR EACH ROW
EXECUTE FUNCTION atualiza_data_cadastro_function();

CREATE TRIGGER atualiza_data_cadastro_genero_roupa
BEFORE INSERT OR UPDATE ON genero_roupa
FOR EACH ROW
EXECUTE FUNCTION atualiza_data_cadastro_function();

CREATE TRIGGER atualiza_data_cadastro_tipos_roupas
BEFORE INSERT OR UPDATE ON tipos_roupas
FOR EACH ROW
EXECUTE FUNCTION atualiza_data_cadastro_function();

CREATE TRIGGER atualiza_data_cadastro_cores
BEFORE INSERT OR UPDATE ON cores
FOR EACH ROW
EXECUTE FUNCTION atualiza_data_cadastro_function();

CREATE TRIGGER atualiza_data_cadastro_tamanhos
BEFORE INSERT OR UPDATE ON tamanhos
FOR EACH ROW
EXECUTE FUNCTION atualiza_data_cadastro_function();

CREATE TRIGGER atualiza_data_cadastro_marcas
BEFORE INSERT OR UPDATE ON marcas
FOR EACH ROW
EXECUTE FUNCTION atualiza_data_cadastro_function();

CREATE TRIGGER atualiza_data_cadastro_tipos_unidades
BEFORE INSERT OR UPDATE ON tipos_unidades
FOR EACH ROW
EXECUTE FUNCTION atualiza_data_cadastro_function();

CREATE TRIGGER atualiza_data_cadastro_itens_estoque
BEFORE INSERT OR UPDATE ON itens_estoque
FOR EACH ROW
EXECUTE FUNCTION atualiza_data_cadastro_function();

CREATE TRIGGER atualiza_data_cadastro_tipos_transacoes
BEFORE INSERT OR UPDATE ON tipos_transacoes
FOR EACH ROW
EXECUTE FUNCTION atualiza_data_cadastro_function();

CREATE TRIGGER atualiza_data_cadastro_transacoes_estoque
BEFORE INSERT OR UPDATE ON transacoes_estoque
FOR EACH ROW
EXECUTE FUNCTION atualiza_data_cadastro_function();

CREATE TRIGGER atualiza_data_cadastro_bancos
BEFORE INSERT OR UPDATE ON bancos
FOR EACH ROW
EXECUTE FUNCTION atualiza_data_cadastro_function();

CREATE TRIGGER atualiza_data_cadastro_agencia_bancos
BEFORE INSERT OR UPDATE ON agencia_bancos
FOR EACH ROW
EXECUTE FUNCTION atualiza_data_cadastro_function();

CREATE TRIGGER atualiza_data_cadastro_contas_bancarias
BEFORE INSERT OR UPDATE ON contas_bancarias
FOR EACH ROW
EXECUTE FUNCTION atualiza_data_cadastro_function();

CREATE TRIGGER atualiza_data_cadastro_cartao_credito
BEFORE INSERT OR UPDATE ON cartao_credito
FOR EACH ROW
EXECUTE FUNCTION atualiza_data_cadastro_function();

CREATE TRIGGER atualiza_data_cadastro_fatura_cartao_credito
BEFORE INSERT OR UPDATE ON fatura_cartao_credito
FOR EACH ROW
EXECUTE FUNCTION atualiza_data_cadastro_function();

CREATE TRIGGER atualiza_data_cadastro_categorias_financeiras
BEFORE INSERT OR UPDATE ON categorias_financeiras
FOR EACH ROW
EXECUTE FUNCTION atualiza_data_cadastro_function();